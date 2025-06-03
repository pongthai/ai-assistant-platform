

from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_proactive_suggestion(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Proactive Suggestion")
    """
    Handle Proactive Suggestion 
    """
    return AssistantResponse(
        intent="proactive_suggestion"

    )
 