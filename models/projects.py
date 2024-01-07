import uuid

from pydantic import BaseModel, Field


class ProjectModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    title: str
    description: str | None
    owner: str
