from fastapi import APIRouter, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Union, Dict, Any
import tempfile, shutil, os

from server.shared.gpt_integration import GPTClient
from server.shared.voice_profile_manager import VoiceProfileManager
from core.audio.tts_manager import TTSManager
from core.utils.usage_tracker_instance import usage_tracker
from server.shared.flow_handlers.intent_router import IntentRouter
from server.shared.intent_classifier.classifier import IntentClassifier
from server.shared.session_manager import session_manager
from core.utils.logger_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

gpt_client = GPTClient()
intent_classifier = IntentClassifier()
intent_router_instance = IntentRouter(gpt_client=gpt_client, intent_classifier=intent_classifier)

vpm = VoiceProfileManager()
tts_manager = TTSManager()

class ChatRequest(BaseModel):
    session_id: str
    user_voice: str

class ChatResponse(BaseModel):
    response: Union[str, Dict[str, Any]]

class SpeakRequest(BaseModel):
    text: str
    is_ssml: bool = False

def cleanup_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"🧹 Deleted: {path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete file: {e}")

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_input: ChatRequest):
    session_id = chat_input.session_id
    session = session_manager.get_session(session_id)
    state_info = session_manager.get_state_info(session_id)

    if state_info and state_info.get("state") and state_info.get("state") != "complete":
        result = intent_router_instance.route_by_state(state_info["state"], chat_input.user_voice, session)
    else:
        result = intent_router_instance.route(chat_input.user_voice, session)

    session_manager.update_session(session_id, intent=session.intent, state=session.state, context_update=session.context)
    logger.info(f"🗣️ {chat_input.user_voice}")
    logger.info(f"🤖 {result}")
    return ChatResponse(response=result)

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

@router.get("/usage")
async def usage_summary():
    summary = usage_tracker.summarize(by="day")
    return JSONResponse(content=summary)

@router.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    if not audio.filename:
        return {"error": "Empty filename"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        shutil.copyfileobj(audio.file, tmp_file)
        temp_path = tmp_file.name

    try:
        speaker = vpm.identify_speaker(temp_path)
        return {"speaker": speaker}
    finally:
        os.remove(temp_path)

@router.post("/create-profile")
async def create_profile(name: str = Form(...), audio: UploadFile = File(...)):
    if not name.strip():
        return {"error": "Missing speaker name"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        shutil.copyfileobj(audio.file, tmp_file)
        temp_path = tmp_file.name

    try:
        vpm.train_profile(name.strip(), temp_path)
        return {"status": "ok", "profile": name.strip()}
    finally:
        os.remove(temp_path)

@router.get("/health")
async def health_check():
    return {"status": "ok"}