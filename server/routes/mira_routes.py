# File: server/routes/mira_routes.py
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from server.mira.models.user_input import AskRequest, ResetSessionRequest
from server.mira.services.session_manager import session_manager
from server.mira.services.prompt_builder import PromptBuilder
from server.mira.services.gpt_client import ask_gpt
from core.audio.tts_manager import TTSManager
from server.vera.services.tts_module import generate_tts
from server.mira.handlers.intent_routes import route_intent
from pathlib import Path
from typing import Optional, List
import uuid
import os
from core.utils.logger_config import get_logger
from server.config.config import OPENAI_API_KEY, OPENAI_MODEL, TTS_PATH

logger = get_logger(__name__)

# Load menu and promotions once at startup
MENU_PATH = Path("server/mira/data/menu.json")
PROMO_PATH = Path("server/mira/data/promotions.json")

with MENU_PATH.open("r", encoding="utf-8") as f:
    MENU_DATA = json.load(f)

with PROMO_PATH.open("r", encoding="utf-8") as f:
    PROMOTIONS = json.load(f)

router = APIRouter()
tts_manager = TTSManager()

# Store session replies temporarily
TEMP_TTS_STORE = {}

def safe_parse_json(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        return None    

@router.post("/ask")
async def ask_user(req: AskRequest):
    prompt_builder = PromptBuilder(MENU_DATA, PROMOTIONS)
    session_id = req.session_id
    user_input = req.user_input.strip()

    # Initialize session if needed
    if not session_manager.has_session(session_id):
        init_prompt = prompt_builder.build_init_prompt()
        session_manager.init_session(session_id, system_prompt=init_prompt)

    # Build prompt
    prompt = prompt_builder.build_user_prompt(user_input)

    # Add user message to history
    session_manager.add_user_message(session_id, prompt)
    messages = session_manager.get_history(session_id)

    # Ask GPT
    reply_text = ask_gpt(messages)
    logger.debug(f"User input: {user_input}, Reply: {reply_text}")
    session_manager.add_assistant_reply(session_id, reply_text)

    try:
        gpt_result = safe_parse_json(reply_text)
        reply_ssml = gpt_result.get("response", reply_text)
        logger.debug(f"GPT reply SSML: {reply_ssml}")
        intent = gpt_result.get("intent", "unknown")      
    except Exception as e:
        intent = "unknown"
        response = reply_text
        result = {"note": "⚠️ GPT reply is not JSON", "error": str(e)}
        logger.error(f"Error processing GPT reply: {result}")

    #tts_path = tts_manager.synthesize(response)

    tts_id = str(uuid.uuid4())
    tts_path = os.path.join(TTS_PATH, f"{tts_id}.mp3")
    generate_tts(reply_ssml, tts_path)
    TEMP_TTS_STORE[tts_id] = tts_path
    logger.info(f"Generated TTS file: {tts_path}")

    return JSONResponse({
        "reply_text": reply_ssml,
        "tts_url": f"/speak/{tts_id}",
        "intent": intent
    })

@router.get("/speak/{tts_id}")
async def speak(tts_id: str):
    logger.info(f"/speak requested: {tts_id}")
    path = TEMP_TTS_STORE.get(tts_id)
    if path and os.path.exists(path):
        logger.info(f"Serving TTS file: {path}")
        return FileResponse(path, media_type="audio/mpeg")
    logger.warning(f"TTS file not found for ID: {tts_id}")
    return JSONResponse({"error": "TTS not found"}, status_code=404)


@router.post("/reset-session")
async def reset_session(req: ResetSessionRequest):
    session_manager.reset_session(req.session_id)
    return {"message": "Session reset"}