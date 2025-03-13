import time
from pathlib import Path
import aiohttp
import json
import os

from fastapi import FastAPI, UploadFile, File, Request, Response, HTTPException
from fastapi.responses import FileResponse
from api.schemas import VersionModel, FeedbackResponse, InstrumentType
from api.logger import setup_logger

from core.preprocessing.preprocessor import AudioProcessor
from core.pitch.basic_pitcher import BasicPitcher
from core.music_submission import SubmissionProcessor
from music21.converter import parse

logger = None

CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:8000")

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


@app.post('/feedback', response_model=FeedbackResponse, description='Анализ исполнения')
async def make_feedback(
    instrument: InstrumentType,
    audio: UploadFile = File(...),
    key: str = "C",
    time_signature: str = "4/4"
):
    try:
        # Создаем временные директории если их нет
        temp_dir = Path("temp")
        processed_dir = temp_dir / "processed"
        output_dir = temp_dir / "output"
        
        for dir_path in [temp_dir, processed_dir, output_dir]:
            dir_path.mkdir(exist_ok=True)
            
        # Генерируем уникальные имена файлов
        timestamp = str(int(time.time()))
        input_path = temp_dir / f"input_{timestamp}.wav"
        processed_path = processed_dir / f"processed_{timestamp}.wav"
        midi_path = output_dir / f"midi_{timestamp}.mid"
        
        # Сохраняем входной файл
        with open(input_path, "wb") as f:
            f.write(await audio.read())
        
        # Предобработка аудио
        processor = AudioProcessor(str(input_path))
        processor.process(output_file=str(processed_path))
        
        # Конвертация в MIDI
        pitcher = BasicPitcher()
        midi_data = pitcher.save_midi(str(processed_path), str(midi_path))
        
        # Формируем данные для chat-service
        chat_data = SubmissionProcessor()
        
        # Отправляем запрос в chat-service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CHAT_SERVICE_URL}/feedback",
                json=chat_data
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Failed to get feedback from chat service"
                    )
                feedback_data = await response.json()
        
        # Очищаем временные файлы
        input_path.unlink()
        processed_path.unlink()
        
        # Формируем ответ
        return FeedbackResponse(
            overall_feedback=feedback_data["overall_feedback"],
            details=feedback_data["details"],
            score=feedback_data["score"],
            visualization_url=feedback_data.get("visualization_url"),
            midi_url=str(midi_path)
        )
        
    except Exception as e:
        await logger.error(f"Error processing feedback request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing feedback request: {str(e)}"
        )