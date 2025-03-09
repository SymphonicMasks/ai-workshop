from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String

Base = declarative_base()


class SystemPrompt(Base):
    __tablename__ = 'system_prompts'
    prompt_id = Column(Integer, primary_key=True, index=True)
    prompt_name = Column(String, nullable=True)
    prompt_text = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
