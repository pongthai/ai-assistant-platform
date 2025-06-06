# File: server/routes/mira_routes.py
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from server.mira.models.user_input import AskRequest, ResetSessionRequest
from server.mira.models.response import AssistantResponse
from server.mira.services.session_manager import session_manager
from server.mira.services.prompt_builder import PromptBuilder
from server.mira.services.gpt_client import ask_gpt  # now async
from core.audio.tts_manager import TTSManager
from server.vera.services.tts_module import generate_tts
from server.mira.handlers.intent_routes import route_intent
from typing import Optional
import uuid
import os
from core.utils.logger_config import get_logger
from server.config.config import OPENAI_API_KEY, OPENAI_MODEL, TTS_PATH

logger = get_logger(__name__)

router = APIRouter()
tts_manager = TTSManager()

# Store session replies temporarily
TEMP_TTS_STORE = {}

def safe_parse_json(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        return None    

@router.post("/ask", response_model=AssistantResponse)
async def ask_user(req: AskRequest):
    logger.debug(f"Received user input[{req.session_id}]: {req.user_input} ")
    session_id = req.session_id
    user_input = req.user_input.strip()

    gpt_reply_text = await ask_gpt(session_id, user_input)
    logger.debug(f"ask_gpt Reply: {gpt_reply_text}")

    try:
        gpt_result = safe_parse_json(gpt_reply_text)
        handler_result = None
        intent = gpt_result.get("intent", "unknown") if gpt_result else "unknown"
        gpt_reply_ssml = gpt_result.get("response", gpt_reply_text) if gpt_result else gpt_reply_text

        handler_result = await route_intent(intent, gpt_result or {}, session_id)
        logger.debug(f"Handler result: {handler_result}")

        if isinstance(handler_result, AssistantResponse):
            reply_ssml = handler_result.response_ssml or gpt_reply_ssml
            intent = handler_result.intent
    except Exception as e:
        intent = "unknown"
        reply_ssml = gpt_reply_ssml
        result = {"note": "⚠️ GPT reply is not JSON", "error": str(e)}
        logger.error(f"Error processing GPT reply: {result}")

    return AssistantResponse(
        intent=intent,
        response_ssml=reply_ssml,
        orders=(
            [order.model_dump() if hasattr(order, "model_dump") else order.dict() if hasattr(order, "dict") else order
             for order in handler_result.orders]
            if isinstance(handler_result, AssistantResponse) and getattr(handler_result, "orders", None) is not None
            else None
        ),
        total_price=getattr(handler_result, "total_price", None),
        discount=getattr(handler_result, "discount", None)
    )

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


# New endpoint: Expose token usage data for a session
@router.get("/token-usage/{session_id}")
async def get_token_usage(session_id: str):
    usage = session_manager.get_token_usage(session_id)
    return usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}