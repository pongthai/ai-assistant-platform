

from server.mira.services.session_manager import session_manager
from fastapi.responses import JSONResponse
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

async def handle_cancel_order(session_id: str):
    if not session_manager.has_session(session_id):
        logger.warning(f"Session not found: {session_id}")
        return JSONResponse({"error": "Session not found"}, status_code=404)

    # Cancel all "new" orders
    order_list = session_manager.get_order_list(session_id)
    canceled_items = []

    for item in order_list:
        if item.status == "new":
            item.status = "canceled"
            canceled_items.append(item.name)

    if not canceled_items:
        logger.info(f"No active 'new' items to cancel for session {session_id}")
        return JSONResponse({
            "intent": "cancel_order",
            "response": "<speak><prosody rate=\"108%\" pitch=\"+1st\">ยังไม่มีรายการที่ยกเลิกได้ค่ะ</prosody></speak>"
        })

    logger.info(f"Canceled items for session {session_id}: {canceled_items}")
    return JSONResponse({
        "intent": "cancel_order",
        "response": f"<speak><prosody rate=\"108%\" pitch=\"+1st\">ยกเลิกรายการ {' และ '.join(canceled_items)} ให้แล้วค่ะ</prosody></speak>"
    })