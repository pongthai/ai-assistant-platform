from server.mira.models.response import AssistantResponse
# from server.mira.handlers.handle_add_order import handle_add_order
# from server.mira.handlers.handle_cancel_order import handle_cancel_order
# from server.mira.handlers.handle_call_staff import handle_call_staff
# from server.mira.handlers.handle_request_bill import handle_request_bill
# from server.mira.handlers.handle_open_topic import handle_open_topic
# from server.mira.handlers.handle_payment_method import handle_payment_method
# from server.mira.handlers.handle_modify_order import handle_modify_order
# from server.mira.handlers.handle_confirm_order import handle_confirm_order
# from server.mira.handlers.handle_recommend_dish import handle_recommend_dish
# from server.mira.handlers.handle_show_menu import handle_show_menu
# from server.mira.handlers.handle_show_promotion import handle_show_promotion
# from server.mira.handlers.handle_suggest_combo import handle_suggest_combo
# from server.mira.handlers.handle_greeting import handle_greeting
# from server.mira.handlers.handle_proactive_suggestion import handle_proactive_suggestion
# from server.mira.handlers.handle_unknow import handle_unknown 
from server.mira.handlers.intent_handlers import *

from core.utils.logger_config import get_logger
import asyncio

logger = get_logger(__name__)

# Mapping of recognized intents to their respective handler functions
INTENT_HANDLERS = {
    "greeting": handle_greeting,
    "add_order": handle_add_order,
    "cancel_order": handle_cancel_order,
    "show_current_order": handle_show_current_order,
    "inquire_total": handle_inquire_total,
    "call_staff": handle_call_staff,
    "request_bill": handle_request_bill,
    "open_topic": handle_open_topic,
    "payment_method": handle_payment_method,
    "modify_order": handle_modify_order,
    "confirm_order": handle_confirm_order,
    "recommend_dish": handle_recommend_dish,
    "show_menu": handle_show_menu,
    "show_promotion": handle_show_promotion,
    "suggest_combo": handle_suggest_combo,
    "proactive_suggestion": handle_proactive_suggestion,
    "unknown": handle_unknown,
    
}

async def route_intent(intent: str, payload: dict, session_id: str) -> AssistantResponse:
    """
    Route the incoming intent to the appropriate handler function.
    Returns an AssistantResponse from the handler, or a fallback if intent is unknown.
    Supports both async and sync handlers.
    """
    handler = INTENT_HANDLERS.get(intent)
    logger.debug(f"route_intent --> Intent: {intent} : handler = {handler} ")
    if handler:
        if asyncio.iscoroutinefunction(handler):
            return await handler(payload, session_id)
        return handler(payload, session_id)
    else:
        logger.debug(f"route-intent : handler is None ")
    return AssistantResponse(
        intent="unknown",
        response_ssml="<speak><prosody rate='108%' pitch='+1st'>ขออภัยค่ะ ไม่เข้าใจความต้องการของคุณ</prosody></speak>"
    )