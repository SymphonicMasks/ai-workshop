from pydantic import (
    BaseModel,
    Field,
)
from typing import List, Tuple


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


class FeedbackRequest(BaseModel):
    """Входные данные для анализа игры"""
    result: List[Tuple[str | None, str | None, str]] = Field(
        ...,
        description='Список кортежей (ожидаемая_нота, сыгранная_нота, тип_ошибки)'
    )