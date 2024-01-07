from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from enums import GardenStatus
from models.base import DateTimeMixin


class GardenModel(Base, DateTimeMixin):
    __tablename__ = "gardens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = mapped_column(String(256), nullable=False)
    address = mapped_column(Text)
    description = mapped_column(Text)
    status: Mapped[GardenStatus] = mapped_column(String(256), default=GardenStatus.SETUP)

