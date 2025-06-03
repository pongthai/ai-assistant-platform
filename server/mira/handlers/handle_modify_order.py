from server.mira.models.order import OrderItem
from server.mira.models.response import AssistantResponse
from server.mira.services.session_manager import session_manager
from core.utils.logger_config import get_logger
from server.mira.services.menu import validate_item, lookup_price

logger = get_logger(__name__) 

def handle_modify_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Modify Order intent") 
    
    if "item" not in payload:
        logger.warning("⚠️ ไม่มีข้อมูล item ใน payload")
        return AssistantResponse(
            intent="modify_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ขอโทษค่ะ ไม่สามารถแก้ไขรายการได้ค่ะ</prosody></speak>"
        )

    item_data = payload["item"]
    if isinstance(item_data, dict):
        item_data = [item_data]

    success_count = 0
    current_orders = session_manager.get_order_list(session_id)

    for item in item_data:
        name = item.get("name")
        delta_qty = item.get("qty")

        if not name or delta_qty is None:
            continue

        if not validate_item(name):
            continue

        existing_item = next((o for o in current_orders if o.name == name), None)

        if not existing_item:
            continue  # No matching item to modify

        new_qty = existing_item.qty + delta_qty

        if new_qty <= 0:
            session_manager.remove_order_item(session_id, name)
            logger.info(f"🗑️ Removed order item: {name}")
        else:
            price = lookup_price(name)
            if price is None:
                continue
            updated_item = OrderItem(name=name, qty=new_qty, price=price)
            session_manager.update_order_item(session_id, updated_item)
            logger.info(f"✏️ Updated order item: {updated_item}")

        success_count += 1

    if success_count == 0:
        return AssistantResponse(
            intent="modify_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ขอโทษค่ะ ไม่พบรายการที่สามารถแก้ไขได้ค่ะ</prosody></speak>"
        )
    else:
        return AssistantResponse(
            intent="modify_order"
        )