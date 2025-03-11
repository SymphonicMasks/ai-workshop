from pydantic import (
    BaseModel,
    Field,
)
from typing import List, Literal


class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')

class NoteResult(BaseModel):
    original_note: str
    played_note: str
    status: Literal["correct", "wrong", "skipped", "duration+", "duration-"]
    original_duration: str
    played_duration: str
    tact_number: int
    start_time: float
    end_time: float


class FeedbackRequest(BaseModel):
    result: List[NoteResult]