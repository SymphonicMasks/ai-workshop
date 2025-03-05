from pydantic import (
    BaseModel,
    Field,
)
from enum import Enum


class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')


class InstrumentType(str, Enum):
    clarnette = "clarnette"
    piano = "piano"
    violin = "violin"
