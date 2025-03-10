import time
from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.responses import FileResponse
from api.schemas import VersionModel
from api.logger import setup_logger

logger = None

app = FastAPI(
    title='ML Service',
    version='0.1',
    description="SympfonicMasks ML Service",
)

@app.on_event("startup")
async def startup_event():
    global logger
    logger = await setup_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    await logger.info(
        f"Incoming request: {request.method} {request.url}\n"
        f"Request body: {body.decode()}"
    )

    response = await call_next(request)
    process_time = time.time() - start_time

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    await logger.info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"
        f"Response body: {response_body.decode()}\n"
        f"Duration: {process_time:.3f}s"
    )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
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


@app.post('/predict/midi', description='Предсказание midi файла из аудио')
async def predict_midi(audio: UploadFile = File(...)) -> FileResponse:
    # Здесь должен быть супер код умный
    return FileResponse('test.mid', filename='result.mid')
