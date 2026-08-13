from pydantic import BaseModel


class Config(BaseModel):
    version: str
