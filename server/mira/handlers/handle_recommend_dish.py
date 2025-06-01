import random
from typing import Optional, List
from server.mira.services.menu import lookup_price, validate_item
from server.mira.models.order import OrderItem
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

def handle_recommend_dish(current_order: List[OrderItem], all_menu: List[dict]) -> Optional[str]:
    if not current_order:
        # General recommendation when no order is made
        candidates = random.sample(all_menu, k=min(2, len(all_menu)))
        names = [item["name"] for item in candidates]
        logger.info(f"🔍 Recommend dishes (no prior order): {names}")
        return f"<speak><prosody rate='108%' pitch='+1st'>แนะนำเมนูพิเศษของเราคือ {' และ '.join(names)} ค่ะ</prosody></speak>"
    else:
        # Recommend based on what has been ordered
        current_names = [order.name for order in current_order]
        related = [item for item in all_menu if item["name"] not in current_names]
        if not related:
            logger.info("✅ All menu items already ordered, no recommendation.")
            return None
        recommended = random.choice(related)
        logger.info(f"🔍 Recommend dish based on current order: {recommended['name']}")
        return f"<speak><prosody rate='108%' pitch='+1st'>คุณอาจจะชอบเมนู {recommended['name']} เพิ่มเติมนะคะ</prosody></speak>"
