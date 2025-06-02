# server/routers/shared_routes.py
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core.audio.tts_manager import TTSManager
import os
from core.utils.logger_config import get_logger

logger = get_logger

router = APIRouter()
tts_manager = TTSManager()

def cleanup_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"🧹 Deleted: {path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete file: {e}")

class SpeakRequest(BaseModel):
    text: str
    is_ssml: bool = False

@router.post("/speak")
async def speak(request: SpeakRequest, background_tasks: BackgroundTasks):
    text = request.text
    is_ssml = request.is_ssml

    try:
        mp3_path = tts_manager.synthesize(text=request.text, is_ssml=request.is_ssml)
        background_tasks.add_task(cleanup_file, mp3_path)
        return FileResponse(mp3_path, media_type="audio/mpeg")
    except Exception as e:
        return {"error": f"TTS failed: {str(e)}"}

@router.get("/")
async def root():
    return {"message": "Shared API is running."}

