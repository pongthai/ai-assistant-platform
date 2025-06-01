from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.requests import Request
from pydantic import BaseModel
from typing import Optional, List
import io
import uuid
import os
import json
import re
import unicodedata

from server.config.config import OPENAI_API_KEY, OPENAI_MODEL, TTS_PATH
from server.vera.services.tts_module import generate_tts
from core.audio.tts_manager import TTSManager
from server.vera.services.prompt_builder import PromptBuilder
from server.vera.services.gpt_client import ask_gpt
from server.vera.services.cleaner import cleanup_old_tts_files
from server.vera.services.session_manager import SessionManager
from server.vera.services.order import OrderItem
from core.utils.logger_config import get_logger


router = APIRouter()
logger = get_logger(__name__)
session_manager = SessionManager()
tts_manager = TTSManager()

# Start background TTS cleaner
cleanup_old_tts_files(ttl_minutes=15, interval_seconds=300)

# Load mock data
with open("server/vera/data/menu.json", "r", encoding="utf-8") as f:
    MENU_DATA = json.load(f)

with open("server/vera/data/promotions.json", "r", encoding="utf-8") as f:
    PROMOTIONS = json.load(f)
    
# Store session replies temporarily
TEMP_TTS_STORE = {}


class AskRequest(BaseModel):
    session_id: str
    user_input: str
    # Add other fields as needed

class ResetSessionRequest(BaseModel):
    session_id: str

class SpeakResponse(BaseModel):
    audio_content: bytes



def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text.strip().lower())

def lookup_price(item_name: str) -> Optional[float]:
    norm_input = normalize_text(item_name)
    for item in MENU_DATA:
        if normalize_text(item["name"]) == norm_input or norm_input in normalize_text(item["name"]):
            return item["price"]
    return None

def validate_item(item_name: str) -> bool:
    norm_input = normalize_text(item_name)
    for item in MENU_DATA:
        norm_menu_name = normalize_text(item["name"])
        if norm_input == norm_menu_name:
            return True
        if norm_input in norm_menu_name:
            return True
        if re.search(rf"^{re.escape(norm_input)}", norm_menu_name):
            return True
    return False

def safe_parse_json(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        return None
    
# Dummy in-memory session store for demonstration
session_history = {}

@router.post("/ask")
async def ask_user(req: AskRequest):
    logger.info(f"/ask received from {req.session_id}: {req.user_input}")
    prompt_builder = PromptBuilder(MENU_DATA, PROMOTIONS)

    if not session_manager.has_session(req.session_id):
        init_prompt = prompt_builder.build_init_prompt()
        session_manager.init_session(req.session_id, system_prompt=init_prompt)

    text = req.user_input.strip()
    order_list = session_manager.get_order_list(req.session_id)

    if text in ["แค่นี้", "ยืนยัน", "สรุป"]:
        prompt = prompt_builder.build_order_summary_prompt(order_list)
    elif text in ["ยกเลิก", "ยกเลิกรายการ"]:
        session_manager.clear_order(req.session_id)
        prompt = prompt_builder.build_cancel_prompt()
    elif text in ["สวัสดี", "เริ่มใหม่"]:
        prompt = prompt_builder.build_greeting_prompt()
    else:
        prompt = prompt_builder.build_user_prompt(text)

    session_manager.add_user_message(req.session_id, prompt)
    messages = session_manager.get_history(req.session_id)

    reply_text = ask_gpt(messages)
    session_manager.add_assistant_reply(req.session_id, reply_text)
    logger.debug(f"GPT reply: {reply_text}")

    gpt_result = safe_parse_json(reply_text)
    if gpt_result:
        intent = gpt_result.get("intent")

        if intent == "add_order" and "item" in gpt_result:
            item_data = gpt_result["item"]

            # 🧠 รองรับทั้ง dict หรือ list
            if isinstance(item_data, dict):
                item_data = [item_data]

            for item in item_data:
                name = item.get("name")
                qty = item.get("qty", 1)

                if not validate_item(name):
                    raise ValueError("Invalid menu item")

                price = lookup_price(name)
                if price is None:
                    raise ValueError("Price not found")

                order_item = OrderItem(name=name, qty=qty, price=price)
                session_manager.add_order_item(req.session_id, order_item)
                logger.info(f"✅ Order added: {order_item}")
                
            if not validate_item(name):
                raise ValueError("Invalid menu item")

            price = lookup_price(name)
            if price is None:
                raise ValueError("Price not found")

            order_item = OrderItem(name=name, qty=qty, price=price)
            session_manager.add_order_item(req.session_id, order_item)
            logger.info(f"✅ Order added: {order_item}")

        reply_ssml = gpt_result.get("response", reply_text)
        logger.debug(f"GPT reply SSML: {reply_ssml}")
        intent = gpt_result.get("intent", "")
    else:
        logger.warning("⚠️ GPT ตอบไม่ใช่ JSON ใช้ข้อความดิบแทน")
        reply_ssml = reply_text
        intent = "unknown"

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

@router.post("/reset-session")
async def reset_session(req: ResetSessionRequest):
    logger.info(f"Resetting session: {req.session_id}")
    session_manager.reset_session(req.session_id)
    return JSONResponse({"message": "Session reset successfully"})

@router.get("/speak/{tts_id}")
async def speak(tts_id: str):
    logger.info(f"/speak requested: {tts_id}")
    path = TEMP_TTS_STORE.get(tts_id)
    if path and os.path.exists(path):
        logger.info(f"Serving TTS file: {path}")
        return FileResponse(path, media_type="audio/mpeg")
    logger.warning(f"TTS file not found for ID: {tts_id}")
    return JSONResponse({"error": "TTS not found"}, status_code=404)

@router.get("/debug-session-history/{session_id}")
async def debug_session_history(session_id: str):
    if not session_manager.has_session(session_id):
        return JSONResponse({"error": "Session not found"}, status_code=404)
    return JSONResponse(session_manager.get_history(session_id))

# export router