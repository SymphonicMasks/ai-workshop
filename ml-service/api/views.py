import time
from pathlib import Path
import aiohttp
import json
import os
import pretty_midi

from fastapi import FastAPI, UploadFile, File, Request, Response, HTTPException
from fastapi.responses import FileResponse
from api.schemas import VersionModel, FeedbackResponse, FeedbackRequest, StructuredFeedback, NoteResult
from api.logger import setup_logger
from core.sheet_music.generator import SheetGenerator

from core.preprocessing.preprocessor_dynamicnr import PianoPreprocessor
from core.pitch.basic_pitcher import BasicPitcher
from core.music_submission import SubmissionProcessor
from config import VISUALIZATIONS_DIR, XMLS_DIR, TEMP_DIR, PROCESSED_DIR, OUTPUT_DIR

logger = None

CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://127.0.0.1:8081")

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
    
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else "unknown"
    }
    
    # Логируем без await и упрощаем данные
    logger.info(f"Request: {log_data['method']} {log_data['url']}")
    
    response = await call_next(request)
    process_time = time.time() - start_time

    # Логируем только статус код
    logger.info(f"Response: {response.status_code} ({process_time:.2f}s)")
    
    return response

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

        await logger.info(f"Creating directories: {[str(p) for p in [VISUALIZATIONS_DIR, XMLS_DIR, TEMP_DIR, PROCESSED_DIR, OUTPUT_DIR]]}")
        VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)
        XMLS_DIR.mkdir(parents=True, exist_ok=True)
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Убираем старые определения путей
        base_dir = Path(__file__).parent.parent
        orig_midi_path = base_dir / "data" / "scores" / "base.midi"

        # Генерируем уникальные имена файлов
        timestamp = str(int(time.time()))
        input_path = TEMP_DIR / f"input_{timestamp}.wav"
        processed_path = PROCESSED_DIR / f"processed_{timestamp}.wav"
        midi_path = OUTPUT_DIR / f"midi_{timestamp}.mid"

        await logger.info(f"File paths:\nInput: {input_path}\nProcessed: {processed_path}\nMIDI: {midi_path}")

        # Сохраняем входной файл
        with open(input_path, "wb") as f:
            f.write(await audio.read())
        await logger.info(f"Input file saved: {input_path} ({input_path.stat().st_size} bytes)")


        await logger.info(f"Starting audio processing: {input_path} -> {processed_path}")
        # Предобработка аудио
        processor = PianoPreprocessor(str(input_path))
        processed_audio, sr = processor.process_pipeline()
        processor.save_output(str(processed_path))
        if not processed_path.exists():
            raise Exception(f"Processed file not created: {processed_path}")
        await logger.info(f"Audio processed: {processed_path} ({processed_path.stat().st_size} bytes)")

        # Конвертация в MIDI
        await logger.info(f"Starting MIDI conversion: {processed_path}")
        pitcher = BasicPitcher()
        submitted_midi_data = pitcher.invoke(str(processed_path))
        orig_midi_data = pretty_midi.PrettyMIDI(str(orig_midi_path))

        sheet_gen = SheetGenerator(
            fractions=[0.125, 0.25, 0.5, 1, 2, 4], 
            pause_fractions=[0.125, 0.25, 0.5, 1, 2, 4], 
            default_path=XMLS_DIR)

        original_stream = sheet_gen.invoke(orig_midi_data)
        notes, tempo = sheet_gen.get_notes_from_midi(submitted_midi_data)

        filename = f"comparison_{timestamp}.xml"
        vis_bath = XMLS_DIR / filename

        submitter = SubmissionProcessor(
            original_stream=original_stream,
            user_notes=notes,
            tempo=tempo,
            viz_path=vis_bath,
            time_signature=(4, 4)
        )
        compared_data_res = submitter.make_viz_new_algo()


        submit_data = FeedbackRequest(
            result=[
                NoteResult(
                    original_note=note["original_note"],
                    played_note=note["played_note"],
                    status=note["status"],
                    original_duration=note["original_duration"],
                    played_duration=note["played_duration"],
                    tact_number=note["tact_number"],
                    start_time=note["start_time"],
                    end_time=note["end_time"]
                ) for note in compared_data_res
            ]
        )

        # Отправляем запрос в chat-service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CHAT_SERVICE_URL}/feedback",
                json=submit_data.dict()
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Failed to get feedback from chat service"
                    )
                feedback_data = await response.json()
        
        
        feedback = StructuredFeedback(**feedback_data)
        # Очищаем временные файлы
        input_path.unlink()
        processed_path.unlink()
        
        

        return {
            "summary": feedback.summary,
            "wrong_parts": feedback.wrong_parts,
            "visualization_filename": filename
        }
        
    except Exception as e:
        await logger.error(f"Error processing feedback request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing feedback request: {str(e)}"
        )

@app.get("/visualization/{filename}")
async def get_visualization(filename: str):
    file_path = XMLS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)