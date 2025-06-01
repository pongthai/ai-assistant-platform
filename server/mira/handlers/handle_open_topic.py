

from fastapi.responses import JSONResponse
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

async def handle_open_topic(session_id: str, user_input: str) -> JSONResponse:
    """
    Handle open-ended user input by responding politely and logging the interaction.
    This does not require structured intent and is used for general conversation.
    """
    logger.info(f"[Open Topic] User says: {user_input} (session: {session_id})")
    response_ssml = f"<speak><prosody rate='108%' pitch='+1st'>{user_input}</prosody></speak>"
    return JSONResponse({
        "intent": "open_topic",
        "reply_text": response_ssml
    })