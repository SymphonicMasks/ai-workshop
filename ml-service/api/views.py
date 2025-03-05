from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

from api.schemas import VersionModel

app = FastAPI(
    title='ML Service',
    version='0.1',
    description="SympfonicMasks ML Service",
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
