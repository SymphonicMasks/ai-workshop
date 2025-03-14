import time
from pathlib import Path
import aiohttp
import json
import os
import pretty_midi

from fastapi import FastAPI, UploadFile, File, Request, Response, HTTPException
from fastapi.responses import FileResponse
from api.schemas import VersionModel, FeedbackResponse, FeedbackRequest, StructuredFeedback
from api.logger import setup_logger
from core.sheet_music.generator import SheetGenerator

from core.preprocessing.preprocessor import AudioProcessor
from core.pitch.basic_pitcher import BasicPitcher
from core.music_submission import SubmissionProcessor

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
async def predict_midi(audio: UploadFile = File()) -> FileResponse:
    # Здесь должен быть супер код умный
    return FileResponse('ml-service\data\violin.xml', filename='result.mid')


@app.post('/feedback', response_model=FeedbackResponse, description='Анализ исполнения')
async def make_feedback(
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
        visualization_xml_dir = "ai-workshop/ml-service/data/visuals"

        
        # Сохраняем входной файл
        with open(input_path, "wb") as f:
            f.write(await audio.read())
        
        # Предобработка аудио
        processor = AudioProcessor(str(input_path))
        processor.process(output_file=str(processed_path))
        
        # Конвертация в MIDI
        pitcher = BasicPitcher()
        submitted_midi_data = pitcher.save_midi(str(processed_path), str(midi_path))
        orig_midi_data = pretty_midi.PrettyMIDI(r"ml-service\data\1\base.midi")
        
        sheet_gen = SheetGenerator(fractions=[0.25, 0.5, 1, 2, 4], pause_fractions=[0.25, 0.5, 1, 2, 4], default_path=Path(visualization_xml_dir))

        original_stream = sheet_gen.invoke(orig_midi_data)
        notes, tempo = sheet_gen.get_notes_from_midi(submitted_midi_data)

        submitter = SubmissionProcessor(original_stream, notes, tempo, visualization_xml_dir)
        compared_data_res = submitter.make_viz_new_algo()

        submit_data = FeedbackRequest({"result": compared_data_res})

        # Отправляем запрос в chat-service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CHAT_SERVICE_URL}/feedback",
                json=submit_data
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Failed to get feedback from chat service"
                    )
                feedback_data = await response.json()
        
        feedback = StructuredFeedback(feedback_data)
        # Очищаем временные файлы
        input_path.unlink()
        processed_path.unlink()
        
        # Формируем ответ
        return FeedbackResponse(
            agent_feedback = feedback,
            shit = FileResponse(visualization_xml_dir / "musicxml.xml")
        )
        
    except Exception as e:
        await logger.error(f"Error processing feedback request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing feedback request: {str(e)}"
        )