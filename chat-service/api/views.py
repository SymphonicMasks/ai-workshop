from fastapi import FastAPI
from fastapi.responses import Response

from api.schemas import VersionModel, FeedbackRequest

app = FastAPI(
    title='Chat Service',
    version='0.1',
    description="SympfonicMasks Chat Service",
)


@app.get(
    '/version',
    description='Возвращает версию API',
    responses={
        200: {'description': 'Версия API', 'content': {'application/json': {'example': '0.1.0'}}}
    }
)
async def get_version() -> VersionModel:
    return VersionModel(
        version=app.version
    )


@app.post('/chat/{sys_prompt_name}', description='Запрос в LLM с системным промытом sys_prompt_id')
async def chat(sys_prompt_name: str, query: str) -> Response:
    # получить системный промпт из какой-то базы
    # prompt = get_sys_prompt_by_name(sys_prompt_name)
    answer = 'Hello, world!'
    return Response(content=answer, media_type="application/text")

@app.post('/feedback')
async def feedback(result: FeedbackRequest) -> Response:
    answer = 'ok'
    return Response(content=answer, media_type="applilcation/text")