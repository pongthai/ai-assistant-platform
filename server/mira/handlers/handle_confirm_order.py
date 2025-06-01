from server.mira.services.session_manager import SessionManager
from server.mira.models.response import AssistantResponse

session_manager = SessionManager()

def handle_confirm_order(session_id: str) -> AssistantResponse:
    order_list = session_manager.get_order_list(session_id)
    if not order_list:
        return AssistantResponse(
            intent="confirm_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>คุณยังไม่มีรายการในออเดอร์ค่ะ</prosody></speak>"
        )

    session_manager.mark_order_confirmed(session_id)

    return AssistantResponse(
        intent="confirm_order",
        response_ssml="<speak><prosody rate='108%' pitch='+1st'>ยืนยันรายการเรียบร้อยแล้วค่ะ กำลังส่งคำสั่งไปยังครัวนะคะ</prosody></speak>"
    )
