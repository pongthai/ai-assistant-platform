from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_show_promotion(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Show Promotion")
    """
    Handle show promotion.
    """
    return AssistantResponse(
        intent="show_promotion"

    )
 