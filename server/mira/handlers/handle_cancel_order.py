from server.mira.models.order import OrderStatus, OrderItem
from server.mira.services.session_manager import session_manager
from fastapi.responses import JSONResponse
from core.utils.logger_config import get_logger
from server.mira.models.response import AssistantResponse

logger = get_logger(__name__)

async def handle_cancel_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Cancel Order")

    if not session_manager.has_session(session_id):
        logger.warning(f"Session not found: {session_id}")
        return AssistantResponse(
            intent="cancel_order",
            response_ssml="<speak><prosody rate=\"108%\" pitch=\"+1st\">ไม่พบข้อมูลออเดอร์ในเซสชันค่ะ</prosody></speak>"
        )

    order_list = session_manager.get_order_list(session_id)
    if not order_list:
        return AssistantResponse(
            intent="cancel_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ไม่พบรายการที่สามารถยกเลิกได้ค่ะ</prosody></speak>"
        )

    session_manager.clear_orders(session_id)
    logger.info(f"Cleared all orders for session {session_id}")

    return AssistantResponse(
        intent="cancel_order"
    )