from pydantic import BaseModel

from enums import DeviceStatus, DeviceTriggerAction
from schemas.base import ORMModel


class DeviceSchema(ORMModel):
    id: int
    title: str
    description: str
    device_type_id: int
    device_type: str
    status: DeviceStatus
    access_token: str
    latest_measure_data: str


class LightbulbDeviceSchema(ORMModel):
    id: int
    title: str
    description: str
    device_type_id: int
    device_type: str
    status: DeviceStatus
    access_token: str
    light_turned_on: bool


class DeviceHistoryItemSchema(BaseModel):
    timestamp: str
    value: str


class DeviceHistorySchema(BaseModel):
    time_unit: str
    value_unit: str
    values: list[DeviceHistoryItemSchema]


class CreateDeviceSchema(BaseModel):
    title: str
    description: str
    device_type_id: int
    garden_id: int


class UpdateDeviceSchema(BaseModel):
    title: str | None
    description: str | None
    device_type_id: int | None
    status: DeviceStatus | None


class PingDeviceSchema(BaseModel):
    access_token: str


class TriggerActionSchema(BaseModel):
    action: DeviceTriggerAction
