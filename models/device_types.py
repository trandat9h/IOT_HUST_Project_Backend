from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from db import Base
from models.base import DateTimeMixin


class DeviceTypeModel(Base, DateTimeMixin):
    __tablename__ = "device_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    measure_data_name: Mapped[str] = mapped_column(String(128), default="")
    unit: Mapped[str] = mapped_column(String(32))
