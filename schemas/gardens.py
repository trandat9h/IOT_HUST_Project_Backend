from pydantic import BaseModel, ConfigDict

from enums import GardenStatus
from schemas.base import ORMModel
from schemas.devices import DeviceSchema


class CreateGardenSchema(BaseModel):
    title: str
    description: str
    address: str


class UpdateGardenSchema(BaseModel):
    title: str | None
    description: str | None
    address: str | None
    status: GardenStatus | None


class GardenSchema(ORMModel):
    id: int
    title: str
    address: str
    description: str
    status: GardenStatus


class GardenDetailSchema(GardenSchema):
    devices: list[DeviceSchema]
