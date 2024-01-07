from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column


from db import Base # noqa


class DateTimeMixin:
    """Created and updated datetime mixin"""

    created = mapped_column(DateTime, default=lambda: datetime.now())
    created._creation_order = 9998
    updated = mapped_column(DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    updated._creation_order = 999