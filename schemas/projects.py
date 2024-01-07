from pydantic import BaseModel


class CreateProjectSchema(BaseModel):
    title: str
    description: str
