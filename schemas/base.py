from pydantic import ConfigDict, BaseModel


class ORMModel(BaseModel):
    class Config:
        orm_mode = True
