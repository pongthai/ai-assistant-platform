from fastapi.responses import JSONResponse
from server.mira.services.session_manager import session_manager

async def handle_call_staff(session_id: str):
    if not session_manager.has_session(session_id):
        return JSONResponse({"error": "Session not found"}, status_code=404)

    response_text = "<speak><prosody rate='108%' pitch='+1st'>เดี๋ยวจะมีพนักงานไปที่โต๊ะของคุณในไม่ช้านะคะ<break time='300ms'/> กรุณารอสักครู่ค่ะ</prosody></speak>"
    return JSONResponse({
        "intent": "call_staff",
        "response": response_text
    })
