from server.mira.handlers.base_handler import BaseIntentHandler
from server.mira.services.menu import lookup_price, validate_item
from server.mira.models.order import OrderItem
from server.mira.models.response import build_response
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

def handle_suggest_combo(session_id: str, session_manager, gpt_result: dict):
    current_order = session_manager.get_order_list(session_id)
    if not current_order:
        logger.warning("🧠 ไม่มีคำสั่งซื้อในระบบเพื่อแนะนำเมนูเพิ่มเติม")
        return build_response(
            intent="suggest_combo",
            ssml_response="<speak><prosody rate='108%' pitch='+1st'>คุณยังไม่ได้สั่งเมนูใดเลยนะคะ</prosody></speak>"
        )

    # Mock recommendation logic: suggest dessert if drink already ordered
    suggested_items = []
    drink_keywords = ["ชา", "กาแฟ", "นม", "โกโก้"]
    dessert_keywords = ["เค้ก", "พาย", "ครัวซองต์"]

    for order_item in current_order:
        for drink in drink_keywords:
            if drink in order_item.name:
                # Suggest dessert
                for menu_item in ["เค้กช็อกโกแลต", "พายแอปเปิ้ล", "ครัวซองต์เนย"]:
                    if validate_item(menu_item):
                        suggested_items.append(menu_item)
                break

    if not suggested_items:
        return build_response(
            intent="suggest_combo",
            ssml_response="<speak><prosody rate='108%' pitch='+1st'>ยังไม่มีเมนูแนะนำเพิ่มเติมในตอนนี้ค่ะ</prosody></speak>"
        )

    suggested_text = "หรือจะลองสั่ง " + " หรือ ".join(suggested_items) + " เพิ่มดูไหมคะ?"
    return build_response(
        intent="suggest_combo",
        ssml_response=f"<speak><prosody rate='108%' pitch='+1st'>{suggested_text}</prosody></speak>"
    )
