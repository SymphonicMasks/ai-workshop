from functools import lru_cache
from typing import Type

from langchain_openai import ChatOpenAI
from pydantic import BaseModel


@lru_cache(maxsize=100)
def get_model(
        model_name: str,
        temperature: float = 0.0,
        output_model: Type[BaseModel] | None = None
    ) -> ChatOpenAI:
    model_kwargs = {} if output_model is None else {"response_format": output_model}
    model = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        model_kwargs=model_kwargs
    )
    return model