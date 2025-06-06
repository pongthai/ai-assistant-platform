
from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_recommend_dish(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle recommend_dishintent.
    """
    return AssistantResponse(
        intent="recommend_dish"

    )
