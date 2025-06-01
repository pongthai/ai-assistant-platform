

import logging
from server.mira.services.session_manager import session_manager
from server.mira.models.order import OrderItem
from server.mira.services.menu import lookup_price, validate_item

logger = logging.getLogger(__name__)

def handle_add_order(payload: dict, session_id: str) -> dict:
    item_data = payload.get("item")
    if not item_data:
        logger.warning("No item data found in payload")
        return {
            "error": "Invalid order request",
            "response": "<speak>ขออภัยค่ะ ไม่พบรายการอาหารที่คุณต้องการสั่ง</speak>"
        }

    if isinstance(item_data, dict):
        item_data = [item_data]

    added_items = []
    for item in item_data:
        name = item.get("name")
        qty = item.get("qty", 1)

        if not validate_item(name):
            logger.warning(f"Invalid menu item: {name}")
            continue

        price = lookup_price(name)
        if price is None:
            logger.warning(f"Price not found for item: {name}")
            continue

        order_item = OrderItem(name=name, qty=qty, price=price)
        session_manager.add_order_item(session_id, order_item)
        added_items.append(order_item)

        logger.info(f"✅ Order added: {order_item}")

    if not added_items:
        return {
            "error": "No valid items added",
            "response": "<speak>ยังไม่มีรายการที่สามารถเพิ่มได้ค่ะ</speak>"
        }

    item_names = " และ ".join([f"{item.qty} {item.name}" for item in added_items])
    return {
        "intent": "add_order",
        "response": f"<speak>รับ {item_names} แล้วค่ะ</speak>"
    }