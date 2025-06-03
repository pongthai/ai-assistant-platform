from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_payment_method(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle payment method intent.
    """
    logger.info(f"[{session_id}] Handling payment method intent")
    logger.debug(f"[{session_id}] Payment method payload: {payload}")
    return AssistantResponse(
        intent="payment_method"
    )