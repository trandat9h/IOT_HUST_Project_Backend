import jwt
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from enums import DeviceStatus
from models.base import DateTimeMixin
from models.device_types import DeviceTypeModel
from models.gardens import GardenModel


class DeviceModel(Base, DateTimeMixin):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("device_types.id"), nullable=False)
    garden_id: Mapped[int] = mapped_column(Integer, ForeignKey("gardens.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[DeviceStatus] = mapped_column(String(64), nullable=False, default=DeviceStatus.SETUP)
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    last_ping = mapped_column(DateTime)

    device_type_model: Mapped[DeviceTypeModel] = relationship(lazy="raise")
    garden: Mapped[GardenModel] = relationship(lazy="raise")

    @property
    def device_type(self) -> str:
        return self.device_type_model.name

    @property
    def access_token(self) -> str:
        payload = {
            "device_id": self.id
        }
        # Generate the JWT token
        return jwt.encode(payload, "secret_key", algorithm='HS256')

    @property
    def light_turned_on(self) -> str:
        return self.meta_data.get('light_turned_on', False)

    @light_turned_on.setter
    def light_turned_on(self, light_turned_on: bool):
        self.meta_data['light_turned_on'] = light_turned_on
