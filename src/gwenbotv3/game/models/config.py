from pydantic import BaseModel


# pylint: disable=missing-class-docstring
class Config(BaseModel):
    version: str
