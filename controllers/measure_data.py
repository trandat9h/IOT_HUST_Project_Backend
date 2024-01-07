from datetime import datetime
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from db import get_session
from engines.devices import get_device_id_by_access_token
from models import DeviceModel
from models.measure_data import MeasureDataModel
from schemas.measure_data import MeasureDataSchema

router = APIRouter(prefix="/measure-data", tags=["measure-data"])


@router.post(
    "/",
    response_description="Receive new data from device",
)
async def receive_new_measure_data(
    data: MeasureDataSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    device_id = get_device_id_by_access_token(data.access_token)
    device = await session.get(DeviceModel, device_id)
    if not device:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Device not found"})

    measure_data = MeasureDataModel(
        device_id=device_id,
        value=data.value,
        timestamp=datetime.now(),
    )

    session.add(measure_data)
    await session.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Data received successfully"})

