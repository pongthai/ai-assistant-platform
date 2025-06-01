

from fastapi.responses import JSONResponse

def handle_payment_method(session_manager, session_id: str, gpt_result: dict):
    # Extract method or ask user to choose
    payment_method = gpt_result.get("payment_method")

    if payment_method:
        reply = f"<speak><prosody rate='108%' pitch='+1st'>รับทราบค่ะ คุณเลือกชำระเงินด้วย {payment_method}</prosody></speak>"
    else:
        reply = (
            "<speak><prosody rate='108%' pitch='+1st'>คุณต้องการชำระเงินด้วยวิธีใดคะ "
            "<break time='300ms'/> เงินสด หรือพร้อมเพย์ หรือคิวอาร์โค้ดคะ</prosody></speak>"
        )

    session_manager.add_assistant_reply(session_id, reply)
    return JSONResponse(content={"reply_text": reply, "intent": "payment_method"})