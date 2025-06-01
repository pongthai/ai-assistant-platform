import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "promotions.json")
with open(os.path.abspath(DATA_PATH), "r", encoding="utf-8") as f:
    PROMOTIONS = json.load(f)

def handle_show_promotion(session_id: str, gpt_response: dict) -> dict:
    if not PROMOTIONS:
        reply_ssml = "<speak><prosody rate='108%' pitch='+1st'>ขออภัยค่ะ ขณะนี้ยังไม่มีโปรโมชั่น</prosody></speak>"
    else:
        promo_lines = [f"<break time='300ms'/>• {p['title']}" for p in PROMOTIONS]
        promo_text = " ".join(promo_lines)
        reply_ssml = f"<speak><prosody rate='108%' pitch='+1st'>ตอนนี้เรามีโปรโมชั่นดังนี้ค่ะ {promo_text}</prosody></speak>"

    return {
        "reply_text": reply_ssml,
        "intent": "show_promotion"
    }
