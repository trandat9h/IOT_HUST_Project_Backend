from datetime import datetime

from pydantic import BaseModel


class MeasureDataSchema(BaseModel):
    access_token: str
    value: str
