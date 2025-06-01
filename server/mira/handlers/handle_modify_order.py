

from server.mira.models.order import OrderItem
from server.mira.services.session_manager import session_manager
from core.utils.logger_config import get_logger
from server.mira.services.menu import validate_item, lookup_price

logger = get_logger(__name__) 

def handle_modify_order(session_id: str, gpt_result: dict) -> str:
    if "item" not in gpt_result:
        logger.warning("⚠️ ไม่มีข้อมูล item ใน gpt_result")
        return "<speak><prosody rate='108%' pitch='+1st'>ขอโทษค่ะ ไม่สามารถแก้ไขรายการได้ค่ะ</prosody></speak>"

    item_data = gpt_result["item"]
    if isinstance(item_data, dict):
        item_data = [item_data]

    success_count = 0
    for item in item_data:
        name = item.get("name")
        qty = item.get("qty")

        if not name or qty is None:
            continue

        if not validate_item(name):
            continue

        if qty <= 0:
            # Remove item
            session_manager.remove_order_item(session_id, name)
            logger.info(f"🗑️ Removed order item: {name}")
        else:
            price = lookup_price(name)
            if price is None:
                continue
            updated_item = OrderItem(name=name, qty=qty, price=price)
            session_manager.update_order_item(session_id, updated_item)
            logger.info(f"✏️ Modified order item: {updated_item}")
        success_count += 1

    if success_count == 0:
        return "<speak><prosody rate='108%' pitch='+1st'>ขอโทษค่ะ ไม่พบรายการที่สามารถแก้ไขได้ค่ะ</prosody></speak>"
    else:
        return "<speak><prosody rate='108%' pitch='+1st'>แก้ไขรายการเรียบร้อยแล้วค่ะ</prosody></speak>"