# Author: <NAME>
# Date: 2021-08-14
# Description: Handle request for bill
# ./handlers/handle_request_bill.py

from fastapi.responses import JSONResponse
from server.mira.services.session_manager import SessionManager

session_manager = SessionManager()

async def handle_request_bill(session_id: str):
    if not session_manager.has_session(session_id):
        return JSONResponse({"error": "Session not found"}, status_code=404)

    reply_ssml = "<speak><prosody rate='108%' pitch='+1st'>รับทราบค่ะ กำลังแจ้งพนักงานให้นำบิลมาให้นะคะ <break time='300ms'/> กรุณารอสักครู่ค่ะ</prosody></speak>"

    return {
        "intent": "request_bill",
        "response": reply_ssml
    }