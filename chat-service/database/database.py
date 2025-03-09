from sqlalchemy import select

from database.models import SystemPrompt


def get_sys_prompt(session, prompt_sys_id: int) -> SystemPrompt:
    res = session.execute(select(SystemPrompt).filter(SystemPrompt.prompt_id == prompt_sys_id))
    return res.scalars().first()


def get_sys_prompt_by_name(session, prompt_name: str) -> SystemPrompt:
    res = session.execute(select(SystemPrompt).filter(SystemPrompt.prompt_name == prompt_name))
    return res.scalars().first()
