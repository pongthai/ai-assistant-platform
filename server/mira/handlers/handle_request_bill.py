
from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_request_bill(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Request Bill")
    """
    Handle request_bill.
    """
    return AssistantResponse(
        intent="request_bill"

    )
 