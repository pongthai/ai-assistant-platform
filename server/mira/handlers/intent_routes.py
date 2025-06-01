from fastapi.responses import JSONResponse
from server.mira.handlers.handle_add_order import handle_add_order
from server.mira.handlers.handle_cancel_order import handle_cancel_order
from server.mira.handlers.handle_call_staff import handle_call_staff
from server.mira.handlers.handle_request_bill import handle_request_bill
from server.mira.handlers.handle_open_topic import handle_open_topic
from server.mira.handlers.handle_payment_method import handle_payment_method
from server.mira.handlers.handle_modify_order import handle_modify_order
from server.mira.handlers.handle_confirm_order import handle_confirm_order
from server.mira.handlers.handle_recommend_dish import handle_recommend_dish
from server.mira.handlers.handle_show_menu import handle_show_menu
from server.mira.handlers.handle_show_promotion import handle_show_promotion
from server.mira.handlers.handle_suggest_combo import handle_suggest_combo
import asyncio

# Mapping of recognized intents to their respective handler functions
INTENT_HANDLERS = {
    "add_order": handle_add_order,
    "cancel_order": handle_cancel_order,
    "call_staff": handle_call_staff,
    "request_bill": handle_request_bill,
    "open_topic": handle_open_topic,
    "request_payment_method": handle_payment_method,
    "modify_order": handle_modify_order,
    "confirm_order": handle_confirm_order,
    "recommend_dish": handle_recommend_dish,
    "show_menu": handle_show_menu,
    "show_promotion": handle_show_promotion,
    "suggest_combo": handle_suggest_combo,
    # Additional intents can be added here
}

async def route_intent(intent: str, payload: dict, session_id: str):
    """
    Route the incoming intent to the appropriate handler function.
    Returns a JSONResponse from the handler, or an error if intent is unknown.
    Supports both async and sync handlers.
    """
    handler = INTENT_HANDLERS.get(intent)
    if handler:
        if asyncio.iscoroutinefunction(handler):
            return await handler(payload, session_id)
        return handler(payload, session_id)
    return JSONResponse({"error": f"Unknown or unsupported intent: {intent}"}, status_code=400)