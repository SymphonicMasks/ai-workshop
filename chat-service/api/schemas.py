from pydantic import (
    BaseModel,
    Field,
)
from typing import List, Tuple


class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')

class FeedbackRequest(BaseModel):
    result: List[Tuple[str | None, str | None, str]]