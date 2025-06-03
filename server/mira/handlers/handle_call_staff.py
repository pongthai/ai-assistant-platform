from server.mira.services.session_manager import session_manager
from server.mira.models.response import AssistantResponse
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

async def handle_call_staff(payload: dict, session_id: str):
    logger.info(f"[{session_id}] Handle Call Staff")
    if not session_manager.has_session(session_id):
        return AssistantResponse(
            intent="call_staff",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ไม่พบข้อมูลเซสชันค่ะ</prosody></speak>"
        )

    return AssistantResponse(
        intent="call_staff",
        response_ssml="<speak><prosody rate='108%' pitch='+1st'>เดี๋ยวจะมีพนักงานไปที่โต๊ะของคุณในไม่ช้านะคะ<break time='300ms'/> กรุณารอสักครู่ค่ะ</prosody></speak>"
    )
