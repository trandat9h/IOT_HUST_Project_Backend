from fastapi import APIRouter
from . import (
    devices,
    gardens,
    device_types,
    measure_data
)


routers = APIRouter()

routers.include_router(devices.router, tags=["devices"])
routers.include_router(gardens.router, tags=["gardens"])
routers.include_router(device_types.router, tags=["device_types"])
routers.include_router(measure_data.router, tags=["measure_data"])



