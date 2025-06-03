

from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_show_menu(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Show Menu")
    """
    Handle Show Menu.
    """
    return AssistantResponse(
        intent="show_menu"

    )
 