from pydantic import (
    BaseModel,
    Field,
)
from enum import Enum
from typing import List, Dict, Optional


class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')


class InstrumentType(str, Enum):
    clarnette = "clarnette"
    piano = "piano"
    violin = "violin"


class FeedbackDetail(BaseModel):
    """Детальная информация об ошибке или рекомендации"""
    type: str = Field(..., description="Тип ошибки или рекомендации")
    message: str = Field(..., description="Текстовое описание")
    timestamp: Optional[float] = Field(None, description="Временная метка в секундах")
    measure: Optional[int] = Field(None, description="Номер такта")
    note: Optional[str] = Field(None, description="Нота, к которой относится замечание")


class FeedbackResponse(BaseModel):
    """Структурированный ответ с рекомендациями"""
    overall_feedback: str = Field(..., description="Общая оценка исполнения")
    details: List[FeedbackDetail] = Field(default_factory=list, description="Список конкретных замечаний")
    score: float = Field(..., description="Общая оценка от 0 до 100")
    visualization_url: Optional[str] = Field(None, description="URL для визуализации ошибок")
    midi_url: Optional[str] = Field(None, description="URL для сравнения MIDI файлов")
    