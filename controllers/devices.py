import calendar
import statistics
from datetime import datetime
from itertools import groupby
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from asyncio_mqtt import Client
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import JSONResponse

from db import get_session
from engines.devices import get_device_latest_measure_data, get_device_id_by_access_token
from enums import DeviceDataGroupBy, DeviceTriggerAction
from models.devices import DeviceModel
from models.measure_data import MeasureDataModel
from schemas.devices import DeviceSchema, DeviceHistorySchema, CreateDeviceSchema, UpdateDeviceSchema, PingDeviceSchema, \
    LightbulbDeviceSchema, TriggerActionSchema

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get(
    "",
    response_model=list[DeviceSchema],
)
async def get_devices_by_garden_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    garden_id: int | None = None,
):
    stmt = select(DeviceModel)
    if garden_id is not None:
        stmt = stmt.where(DeviceModel.garden_id == garden_id)

    stmt = stmt.options(selectinload(DeviceModel.device_type_model))

    devices = (await session.scalars(stmt)).all()

    sensor_devices = [device for device in devices if device.device_type.startswith('sensor_')]

    response = []
    for device in sensor_devices:
        response.append({
            **device.__dict__,
            "device_type": device.device_type,
            "access_token": device.access_token,
            'latest_measure_data': await get_device_latest_measure_data(session, device),
        })

    return response


@router.get(
    "/lightbulbs",
    response_model=list[LightbulbDeviceSchema],
)
async def get_lightbulb_devices(
    session: Annotated[AsyncSession, Depends(get_session)],
    garden_id: int | None = None,
):
    stmt = select(DeviceModel)
    if garden_id is not None:
        stmt = stmt.where(DeviceModel.garden_id == garden_id)

    stmt = stmt.options(selectinload(DeviceModel.device_type_model))

    devices = (await session.scalars(stmt)).all()

    return [
        {
            **device.__dict__,
            "device_type": device.device_type,
            "access_token": device.access_token,
            "light_turned_on": device.light_turned_on,
        }
        for device in devices if device.device_type.startswith('lightbulb')
    ]


@router.get(
    "/{device_id}",
    response_model=DeviceSchema,
)
async def get_device_by_id(
    device_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    device: DeviceModel | None = await session.get(DeviceModel, device_id)
    if not device:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Device not found"}),
        )

    await session.refresh(device, ["device_type_model"])

    return {
        **device.__dict__,
        "device_type": device.device_type,
        "access_token": device.access_token,
        'latest_measure_data': await get_device_latest_measure_data(session, device)
    }


@router.post(
    "/{device_id}/trigger",
    description="Turn on/off lightbulb",
)
async def trigger_lightbulb(
    device_id: int,
    data: TriggerActionSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    device: DeviceModel | None = await session.get(DeviceModel, device_id)
    if not device:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Device not found"}),
        )

    light_turn_on = data.action == DeviceTriggerAction.TURN_ON
    device.light_turned_on = light_turn_on
    await session.commit()

    # publish event
    async with Client("broker.hivemq.com") as client:
        await client.publish("hust-iot-lightbulbs", payload="1" if light_turn_on else "0")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "Lightbulb triggered"}),
    )


@router.post(
    "/pings",
)
async def ping_device(
    data: PingDeviceSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    device_id = get_device_id_by_access_token(data.access_token)
    device: DeviceModel | None = await session.get(DeviceModel, device_id)
    if not device:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Device not found"}),
        )

    device.last_ping = datetime.now()
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "Device pinged"}),
    )


@router.get(
    "/{device_id}/history",
    response_model=DeviceHistorySchema,
)
async def get_device_history(
    group_by: DeviceDataGroupBy,
    group_value: datetime,
    device_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    device = await session.get(DeviceModel, device_id)
    if not device:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Device not found"}),
        )

    if group_by == DeviceDataGroupBy.HOUR:
        # Get the beginning of the day (midnight)
        start_of_day = datetime.combine(group_value, datetime.min.time())
        # Get the end of the day (23:59:59.999999)
        end_of_day = datetime.combine(group_value, datetime.max.time())
        selected_range = (start_of_day, end_of_day)
    elif group_by == DeviceDataGroupBy.DAY:
        # Get the first day of the month with beginning hour and minute
        first_day = group_value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate the last day of the month
        _, last_day_of_month = calendar.monthrange(group_value.year, group_value.month)
        last_day = group_value.replace(day=last_day_of_month, hour=23, minute=59, second=59, microsecond=999999)

        selected_range = (first_day, last_day)
    elif group_by == DeviceDataGroupBy.MONTH:
        # Get the first day of the year with beginning hour and minute
        first_day = group_value.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate the last day of the year
        last_day = group_value.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

        selected_range = (first_day, last_day)
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": "Invalid group_by value"}),
        )

    stmt = (
        select(MeasureDataModel)
        .where(MeasureDataModel.device_id == device_id)
        .where(MeasureDataModel.timestamp.between(*selected_range))
        .order_by(MeasureDataModel.timestamp.asc())
    )

    def calculate_hourly_median(_data: list[MeasureDataModel]):
        # Group data by hour
        grouped_data = {hour: list(group) for hour, group in groupby(_data, key=lambda x: x.timestamp.hour)}

        # Calculate median for each group
        hourly_medians = {}
        for hour, group in grouped_data.items():
            values = [float(item.value) for item in group]
            mean_value = statistics.mean(values)
            hourly_medians[hour] = round(mean_value, 2)

        full_hourly_medians = [
            {
                'timestamp': f"{hour}:00",
                'value': hourly_medians[hour],
            }
            if hour in hourly_medians
            else {
                'timestamp': f"{hour}:00",
                'value': "0.0",
            }
            for hour in range(24)
        ]

        return full_hourly_medians

    def calculate_daily_median(_data: list[MeasureDataModel]):
        # Group data by day
        grouped_data = {day: list(group) for day, group in groupby(_data, key=lambda x: x.timestamp.day)}

        # Get a list of days in the month
        _, last_day_of_month = calendar.monthrange(group_value.year, group_value.month)
        days_in_month = list(range(1, last_day_of_month + 1))


        # Calculate median for each group
        daily_medians = {}
        for day, group in grouped_data.items():
            values = [float(item.value) for item in group]
            mean_value = statistics.mean(values)
            daily_medians[day] = round(mean_value, 2)

        full_daily_medians = [
            {
                'timestamp': f"{day}",
                'value': daily_medians[day],
            }
            if day in daily_medians
            else
            {
                'timestamp': f"{day}",
                'value': "0.0",
            }
            for day in days_in_month
        ]

        return full_daily_medians

    def calculate_monthly_median(_data: list[MeasureDataModel]):
        # Group data by month
        grouped_data = {month: list(group) for month, group in groupby(_data, key=lambda x: x.timestamp.month)}

        # Calculate median for each group
        monthly_medians = {}
        for month, group in grouped_data.items():
            values = [float(item.value) for item in group]
            mean_value = statistics.mean(values)
            monthly_medians[month] = round(mean_value, 2)

        full_monthly_medians = [
            {
                'timestamp': f"{month}",
                'value': monthly_medians[month],
            }
            if month in monthly_medians
            else {
                'timestamp': f"{month}",
                'value': "0.0",
            }
            for month in range(1, 13)
        ]

        return full_monthly_medians

    data = (await session.scalars(stmt)).all()

    group_by_to_function = {
        DeviceDataGroupBy.HOUR: calculate_hourly_median,
        DeviceDataGroupBy.DAY: calculate_daily_median,
        DeviceDataGroupBy.MONTH: calculate_monthly_median,
    }

    group_by_to_time_unit = {
        DeviceDataGroupBy.HOUR: 'hour',
        DeviceDataGroupBy.DAY: 'day',
        DeviceDataGroupBy.MONTH: 'month',
    }

    await session.refresh(device, ["device_type_model"])
    value_unit = device.device_type_model.unit

    return {
        'time_unit': group_by_to_time_unit[group_by],
        'value_unit': value_unit,
        'values': group_by_to_function[group_by](list(data)),
    }


@router.post(
    "",
    response_model=DeviceSchema,
)
async def create_device(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: CreateDeviceSchema,
):
    device = DeviceModel(**data.dict())

    session.add(device)
    await session.commit()
    await session.refresh(device, ["device_type_model"])

    return {
        **device.__dict__,
        "device_type": device.device_type,
        "access_token": device.access_token,
        'latest_measure_data': await get_device_latest_measure_data(session, device)
    }


@router.delete(
    "/{device_id}",
    response_model=DeviceSchema,
)
async def delete_device(
    session: Annotated[AsyncSession, Depends(get_session)],
    device_id: int,
):
    device = await session.get(DeviceModel, device_id)

    await session.delete(device)

    return device


@router.put(
    "/{device_id}",
    response_model=DeviceSchema,
)
async def update_device(
    session: Annotated[AsyncSession, Depends(get_session)],
    device_id: int,
    data: UpdateDeviceSchema,
):
    device: DeviceModel | None = await session.get(DeviceModel, device_id)
    await session.refresh(device, ["device_type_model"])

    if not device:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Device not found"}),
        )

    if data.title is not None:
        device.title = data.title
    if data.description is not None:
        device.description = data.description
    if data.device_type_id is not None:
        device.device_type_id = data.device_type_id
    if data.status is not None:
        device.status = data.status

    await session.commit()

    return {
        **device.__dict__,
        "device_type": device.device_type,
        'latest_measure_data': await get_device_latest_measure_data(session, device)
    }
