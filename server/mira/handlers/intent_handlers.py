from server.mira.services.session_manager import session_manager
from server.mira.models.order import OrderItem, OrderStatus
from server.mira.services.menu import lookup_price, validate_item
from server.mira.models.response import AssistantResponse
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

intent_list = """
🔹 Action Category:
- greeting: Greet the customer
- call_staff: Call a staff member
- request_bill: Request the bill
- payment_method: Ask or specify the payment method


🔹 Order Category:
- add_order: Add menu item to the order
- cancel_order: Cancel all unprocessed items
- modify_order: Modify or cancel specific items
- confirm_order: Confirm the order to proceed
- show_current_order: Ask to review current or past order items
- inquire_total: Ask for total price of the order

🔹 Information Category:
- show_menu: Request the full menu
- show_promotion: Request available promotions
- recommend_dish: Ask for menu recommendations
- suggest_combo: Suggest combos or pairings with current order

🔹 Other:
- proactive_suggestion: System-initiated menu suggestion
- open_topic: General conversation
- unknown: Unable to determine intent
""".strip()

#####  Order Category ######
def handle_add_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Add Order")
    item_data = payload.get("item")
    if not item_data:
        logger.warning("No item data found in payload")
        return AssistantResponse(
            intent="add_order",
            response_ssml="<speak>ขออภัยค่ะ ไม่พบรายการอาหารที่คุณต้องการสั่ง</speak>"
        )

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

        # Check for existing item in the session
        existing_orders = session_manager.get_order_list(session_id)
        existing_item = next((o for o in existing_orders if o.name == name), None)

        if existing_item:
            new_qty = existing_item.qty + qty
            updated_item = OrderItem(name=name, qty=new_qty, price=price)
            session_manager.update_order_item(session_id, updated_item)
            logger.info(f"✏️ Updated existing order: {updated_item}")
            added_items.append(updated_item)
        else:
            order_item = OrderItem(name=name, qty=qty, price=price)
            session_manager.add_order_item(session_id, order_item)
            logger.info(f"✅ New order added: {order_item}")
            added_items.append(order_item)

    if not added_items:
        return AssistantResponse(
            intent="add_order",
            response_ssml="<speak>ยังไม่มีรายการที่สามารถเพิ่มได้ค่ะ</speak>"
        )

    item_names = " และ ".join([f"{item.qty} {item.name}" for item in added_items])
    # Extract total_price and discount from payload, validate total
    total_price = str(payload.get("total_price", 0))
    discount = str(payload.get("discount",0)  )
    calculated_total = sum([item.price * item.qty for item in session_manager.get_order_list(session_id)])
    logger.debug(f"Total price: {total_price}, discount: {discount} , calculated_total={calculated_total}")

    return AssistantResponse(
        intent="add_order",
        orders=[order.model_dump() for order in session_manager.get_order_list(session_id)],
        total_price=total_price,
        discount=discount
    )

async def handle_cancel_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Cancel Order")

    if not session_manager.has_session(session_id):
        logger.warning(f"Session not found: {session_id}")
        return AssistantResponse(
            intent="cancel_order",
            response_ssml="<speak><prosody rate=\"108%\" pitch=\"+1st\">ไม่พบข้อมูลออเดอร์ในเซสชันค่ะ</prosody></speak>"
        )

    order_list = session_manager.get_order_list(session_id)
    if not order_list:
        return AssistantResponse(
            intent="cancel_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ไม่พบรายการที่สามารถยกเลิกได้ค่ะ</prosody></speak>"
        )

    session_manager.clear_orders(session_id)
    logger.info(f"Cleared all orders for session {session_id}")
    # Extract total_price and discount from payload, validate total
    total_price = str(payload.get("total_price", 0))
    discount = str(payload.get("discount",0)  )
    calculated_total = sum([item.price * item.qty for item in session_manager.get_order_list(session_id)])
    logger.debug(f"Total price: {total_price}, discount: {discount} , calculated_total={calculated_total}")

    return AssistantResponse(
        intent="cancel_order",
        orders=[order.model_dump() for order in session_manager.get_order_list(session_id)],
        total_price=total_price,
        discount=discount
    )

def handle_confirm_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Confirm Order")

    order_list = session_manager.get_order_list(session_id)
    if not order_list:
        return AssistantResponse(
            intent="confirm_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>คุณยังไม่มีรายการในออเดอร์ค่ะ</prosody></speak>"
        )
    
    for order_item in order_list:
        if order_item.status == OrderStatus.new:
            order_item.status = OrderStatus.in_progress
    # Extract total_price and discount from payload, validate total
    total_price = str(payload.get("total_price", 0))
    discount = str(payload.get("discount",0)  )
    calculated_total = sum([item.price * item.qty for item in session_manager.get_order_list(session_id)])
    logger.debug(f"Total price: {total_price}, discount: {discount} , calculated_total={calculated_total}")

    return AssistantResponse(
        intent="confirm_order",
        orders=[order.model_dump() for order in session_manager.get_order_list(session_id)],
        total_price=total_price,
        discount=discount
    )

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
        qty = item.get("qty")
        price = item.get("price")

        if not name or qty is None or price is None:
            continue

        if not validate_item(name):
            continue

        existing_item = next((o for o in current_orders if o.name == name), None)

        if not existing_item:
            continue  # No matching item to modify

        if qty <= 0:
            session_manager.remove_order_item(session_id, name)
            logger.info(f"🗑️ Removed order item: {name}")
        else:
            updated_item = OrderItem(name=name, qty=qty, price=price)
            session_manager.update_order_item(session_id, updated_item)
            logger.info(f"✏️ Updated order item: {updated_item}")

        success_count += 1

    if success_count == 0:
        return AssistantResponse(
            intent="modify_order",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ขอโทษค่ะ ไม่พบรายการที่สามารถแก้ไขได้ค่ะ</prosody></speak>"
        )
    else:
        # Extract total_price and discount from payload, validate total
        total_price = str(payload.get("total_price", 0))
        discount = str(payload.get("discount",0)  )
        calculated_total = sum([item.price * item.qty for item in session_manager.get_order_list(session_id)])
        logger.debug(f"Total price: {total_price}, discount: {discount} , calculated_total={calculated_total}")

        
        return AssistantResponse(
            intent="modify_order",
            orders=[order.model_dump() for order in session_manager.get_order_list(session_id)],
            total_price=total_price,
            discount=discount
        )

async def handle_show_current_order(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle show_current_order")
    """
    Handle show_current_order.
    """
    return AssistantResponse(
        intent="show_current_order"

    )

async def handle_inquire_total(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle inquire_total")
    """
    Handle inquire_total.
    """
    return AssistantResponse(
        intent="inquire_total"

    )


##### Action Category ######

async def handle_greeting(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Greeting")
    """
    Handle Greeting.
    """
    return AssistantResponse(
        intent="greeting"

    )
 
async def handle_call_staff(payload: dict, session_id: str):
    logger.info(f"[{session_id}] Handle Call Staff")
    if not session_manager.has_session(session_id):
        return AssistantResponse(
            intent="call_staff",
            response_ssml="<speak><prosody rate='108%' pitch='+1st'>ไม่พบข้อมูลเซสชันค่ะ</prosody></speak>"
        )

    return AssistantResponse(
        intent="call_staff"
    )

async def handle_payment_method(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle payment method intent.
    """
    logger.info(f"[{session_id}] Handling payment method intent")
    logger.debug(f"[{session_id}] Payment method payload: {payload}")
    return AssistantResponse(
        intent="payment_method"
    )

async def handle_request_bill(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Request Bill")
    """
    Handle request_bill.
    """
    return AssistantResponse(
        intent="request_bill"

    )
 

##### Information Category ######
async def handle_recommend_dish(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle recommend_dishintent.
    """
    return AssistantResponse(
        intent="recommend_dish"

    )

async def handle_show_menu(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Show Menu")
    """
    Handle Show Menu.
    """
    return AssistantResponse(
        intent="show_menu"

    )
 
async def handle_show_promotion(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Show Promotion")
    """
    Handle show promotion.
    """
    return AssistantResponse(
        intent="show_promotion"

    )
 
async def handle_suggest_combo(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Suggest Combo")
    """
    Handle Suggest Combo.
    """
    return AssistantResponse(
        intent="suggest_combo"

    )
 


##### Other ######
async def handle_open_topic(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle open-ended user input by responding politely and logging the interaction.
    This does not require structured intent and is used for general conversation.
    """
    logger.info(f"[{session_id}] Open topic from user")
    user_input = payload.get("user_input", "")
    logger.debug(f"[{session_id}] Open topic from user: {user_input}")

    return AssistantResponse(
        intent="open_topic"
    )

async def handle_proactive_suggestion(payload: dict, session_id: str) -> AssistantResponse:
    logger.info(f"[{session_id}] Handle Proactive Suggestion")
    """
    Handle Proactive Suggestion 
    """
    return AssistantResponse(
        intent="proactive_suggestion"

    )
 
async def handle_unknown(payload: dict, session_id: str) -> AssistantResponse:
    """
    Handle open-ended user input by responding politely and logging the interaction.
    This does not require structured intent and is used for general conversation.
    """
    logger.info(f"[{session_id}] handle unknown")

    return AssistantResponse(
        intent="unknown"
    )
