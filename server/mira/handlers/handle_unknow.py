from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_unknown(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle open-ended user input by responding politely and logging the interaction.
    This does not require structured intent and is used for general conversation.
    """
    logger.info(f"[{session_id}] handle unknown")

    return AssistantResponse(
        intent="unknown"
    )