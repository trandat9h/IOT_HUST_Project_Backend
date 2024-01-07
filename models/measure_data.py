from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from models.base import DateTimeMixin


class MeasureDataModel(Base, DateTimeMixin):
    __tablename__ = "measure_datas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now())
    value: Mapped[str] = mapped_column(String(256), nullable=False)
