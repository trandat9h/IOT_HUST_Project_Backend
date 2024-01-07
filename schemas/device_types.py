from pydantic import BaseModel

from schemas.base import ORMModel


class DeviceTypeSchema(ORMModel):
    id: int
    name: str
    unit: str | None


class CreateDeviceTypeSchema(BaseModel):
    name: str
    unit: str | None


class UpdateDeviceTypeSchema(BaseModel):
    name: str | None
    unit: str | None
