from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_open_topic(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle open-ended user input by responding politely and logging the interaction.
    This does not require structured intent and is used for general conversation.
    """
    logger.info(f"[{session_id}] Open topic from user")
    user_input = payload.get("user_input", "")
    logger.debug(f"[{session_id}] Open topic from user: {user_input}")

    return AssistantResponse(
        intent="open_topic"
    )