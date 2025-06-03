from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_suggest_combo(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Suggest Combo")
    """
    Handle Suggest Combo.
    """
    return AssistantResponse(
        intent="suggest_combo"

    )
 