from enum import Enum


class GardenStatus(str, Enum):
    SETUP = 'setup'
    ACTIVE = 'active'
    ARCHIVED = 'archived'


class DeviceStatus(str, Enum):
    SETUP = 'setup'
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ERROR = 'error'


class DeviceDataGroupBy(str, Enum):
    HOUR = 'hour'
    DAY = 'day'
    MONTH = 'month'


class DeviceTriggerAction(str, Enum):
    TURN_ON = 'turn_on'
    TURN_OFF = 'turn_off'