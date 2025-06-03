from server.mira.services.session_manager import session_manager
from server.mira.models.response import AssistantResponse
from server.mira.models.order import OrderStatus
from core.utils.logger_config import get_logger
logger = get_logger(__name__)
 
def handle_confirm_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Confirm Order")

    order_list = session_manager.get_order_list(session_id)
    if not order_list:
        return AssistantResponse(
            intent="confirm_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>คุณยังไม่มีรายการในออเดอร์ค่ะ</prosody></speak>"
        )
    
    for order_item in order_list:
        if order_item.status == OrderStatus.new:
            order_item.status = OrderStatus.in_progress

    return AssistantResponse(
        intent="confirm_order"
    )
