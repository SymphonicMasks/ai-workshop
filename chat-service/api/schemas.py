from pydantic import (
    BaseModel,
    Field,
)
from typing import List, Literal


class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')


class WrongPartFeedback(BaseModel):
    """Структура для описания ошибки в конкретном такте"""
    tact_index: int = Field(..., description='Номер такта, где была допущена ошибка')
    feedback: str = Field(..., description='Короткое описание ошибки и совет по исправлению')


class StructuredFeedback(BaseModel):
    """Структурированный отзыв об игре"""
    summary: str = Field(
        ...,
        description='Краткое общее описание качества исполнения, включая процент успешных нот'
    )
    wrong_parts: List[WrongPartFeedback] = Field(
        default_factory=list,
        description='Список конкретных ошибок по тактам'
    )


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