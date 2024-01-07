from sqlalchemy import select
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from db import get_session
from models.device_types import DeviceTypeModel
from schemas.device_types import DeviceTypeSchema, CreateDeviceTypeSchema

router = APIRouter(prefix="/device-types", tags=["device-types"])


@router.get(
    "/",
    response_model=list[DeviceTypeSchema],
)
async def get_device_types(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    stmt = select(DeviceTypeModel)

    device_types = (await session.scalars(stmt)).all()

    for _type in device_types:
        _type.name = _type.name.replace("sensor_", "")

    return device_types


@router.post(
    "/",
    response_model=DeviceTypeSchema,
)
async def create_device_type(
    data: CreateDeviceTypeSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    data.name = f"sensor_{data.name}"
    new_type = DeviceTypeModel(**data.dict())

    session.add(new_type)
    await session.commit()

    return new_type


@router.put(
    "/{device_type_id}",
    response_model=DeviceTypeSchema,
)
async def update_device_type(
    device_type_id: int,
    data: CreateDeviceTypeSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    device_type = await session.get(DeviceTypeModel, device_type_id)

    if not device_type:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Device type not found"})

    if data.name:
        device_type.name = f"sensor_{data.name}"
    if data.unit:
        device_type.unit = data.unit

    await session.commit()

    return device_type


