from pathlib import Path
import json
from server.mira.models.order import OrderStatus
from server.mira.handlers.intent_handlers import intent_list

from core.utils.logger_config import get_logger
logger = get_logger(__name__)

# Load menu and promotions once at startup
MENU_PATH = Path("server/mira/data/menu.json")
PROMO_PATH = Path("server/mira/data/promotions.json")
RECOMMENDATIONS_PATH = Path("server/mira/data/recommendations.json")

with MENU_PATH.open("r", encoding="utf-8") as f:
    MENU_DATA = json.load(f)

with PROMO_PATH.open("r", encoding="utf-8") as f:
    PROMOTIONS = json.load(f)

with RECOMMENDATIONS_PATH.open("r", encoding="utf-8") as f:
    RECOMMENDATIONS = json.load(f)

class PromptBuilder:
    def __init__(self):
        logger.info("Initialzing PromptBuilder")
        self.menu = MENU_DATA
        self.promotions = PROMOTIONS
        self.recommendations = RECOMMENDATIONS

    def get_menu_items(self, with_price=True, as_json=False, limit=None):
        items = self.menu[:limit] if limit else self.menu
        if as_json:
            return [{"name": item["name"], "price": item["price"]} for item in items] if with_price else [{"name": item["name"]} for item in items]
        if with_price:
            return [f"{item['name']} ({item['price']} บาท)" for item in items]
        else:
            return [f"{item['name']}" for item in items]
    
    def get_promotion_text(self, limit=None):
      promos = self.promotions[:limit] if limit else self.promotions
      return "\n".join([f"- {p}" for p in promos])

    def build_init_prompt(self):
        logger.debug("enter build_init_prompt")
        return f"""
You are MIRA, an AI assistant located on a restaurant table. Your main responsibilities are:

- Politely assisting users with questions in the context of a restaurant  
- Helping users order food and drinks  
- Summarizing current orders clearly when needed  

Please respond using **JSON format only** with one of the supported intent labels below.

If your response includes spoken output, it must use the following SSML structure:  
<speak><prosody rate="110%" pitch="+1st">...</prosody><break time="300ms"/></speak>

### Supported intents:
{intent_list}

⚠️ **Restrictions**:
- Do not invent or use new intent names  
- Do not suggest menu items that are not in the current system  
- Do not include explanations or comments outside the JSON block  
- Do not use ``` or ```json to wrap the JSON  

### Example of a correct response:
{{
  "intent": "greeting",
  "response": "<speak><prosody rate='110%' pitch='+1st'>สวัสดีค่ะ</prosody></speak>"
}}
""".strip()

    def _get_recommendations_from_order(self, order_list):
        if not order_list:
            return ""
        suggested = []
        for item in order_list:
            item_id = getattr(item, "id", None)
            if not item_id:
                continue
            recs = self.recommendations.get("based_on_order", {}).get(item_id, [])
            for rec in recs:
                suggested.append(f"- {rec['id']}: {rec['reason']}")
        if suggested:
            return "\n\nเมนูแนะนำเพิ่มเติมจากรายการที่สั่ง:\n" + "\n".join(suggested)
        return ""

    def aggregate_order(self, order_list):
        from collections import defaultdict
        counter = defaultdict(int)
        for item in order_list:
            logger.debug(f"aggregate_order : order=[{getattr(item, 'name', None)},  {getattr(item, 'qty', 1)}, {getattr(item, 'status', None)}] ")
            if getattr(item, "status", None) == OrderStatus.canceled:
                continue
            name = getattr(item, "name", None)
            qty = getattr(item, "qty", 1)
            counter[name] += qty
        return [f"- {name} x {qty} ({self._get_price_by_name(name)} บาท)" for name, qty in counter.items()]

    def aggregate_order_json(self, order_list):
        from collections import defaultdict
        counter = defaultdict(int)
        for item in order_list:
            if getattr(item, "status", None) == OrderStatus.canceled:
                continue
            name = getattr(item, "name", None)
            qty = getattr(item, "qty", 1)
            counter[name] += qty

        result = []
        for name, qty in counter.items():
            price = self._get_price_by_name(name)
            result.append({
                "name": name,
                "qty": qty,
                "price": price
            })
        return result

    def _get_price_by_name(self, name):
        for item in self.menu:
            if item["name"] == name:
                return item["price"]
        return "N/A"

    def build_user_prompt(self, user_input, order_list=None):
        logger.debug("enter build_user_prompt")

        order_text = ""
        if order_list:
            aggregated = self.aggregate_order_json(order_list)
            logger.debug(f"build_user_prompt aggregate_order_json: aggregated = {aggregated}")
            formatted_orders = [f"- {item['name']} x {item['qty']} ({item['price']} บาท)" for item in aggregated]
            order_text = "\n\nรายการที่ลูกค้าสั่งแล้ว:\n" + "\n".join(formatted_orders)
        recommendation_text = self._get_recommendations_from_order(order_list)

        return f"""
### Context
User: {user_input}

user orders:
{order_text}

recommendations on menu:
{recommendation_text}

### Instructions:
Please respond with the appropriate intent in JSON format only.  
- Do not create new intent names  
- Do not include any explanation or extra text outside the JSON  
- Do not use ``` or ```json to wrap the JSON  
- If there is an opportunity to proactively suggest additional menu items (e.g., items that pair well with the order or help fulfill a promotion), use intent = proactive_suggestion
- You should calculate total price and apply relevant discounts from the promotion list if applicable.

### Speech format:
- If the response is spoken text, use SSML: <speak><prosody rate="110%" pitch="+1st">...</prosody></speak> and include <break time="300ms"/> for pause

### Example:
{{
  "intent": "add_order",
  "item": {{ "name": "ข้าวผัดกุ้ง", "qty": 1, "price": 60 }},
  "response": "<speak><prosody rate='110%' pitch='+1st'>รับข้าวผัดกุ้ง 1 ที่นะคะ <break time='300ms'/> เพิ่มอะไรอีกไหมคะ?</prosody></speak>",
  "total_price": 170,
  "discount": 10
}}
### Notes:
- "total_price" is the sum after applying any discounts.
- "discount" is the value of the discount applied, if any (0 if no discount).
""".strip()
    
    def build_intent_detection_prompt(self, user_input: str) -> str:
      """
      Build a prompt to detect high-level intent and how broad the menu info scope should be.
      """
      return f"""
You are an AI assistant in a restaurant. Your task is to identify the user's intent from the list below, assign a confidence score (from 0.0 to 1.0), and determine the appropriate level of menu/promotion detail to present.

🔹 Intent categories:
- greeting: Greeting the user, e.g. "Hello"
- order: Commad to add/modify/cancel an order, asking for order details/summary, asking for bill e.g. "One can of Coke please"
- menu_info: Asking about the menu, e.g. "What do you have?"
- promotion: Asking about promotions, e.g. "Any specials?"
- call_staff: Calling a staff member, e.g. "Can you get the staff?"
- social: General conversation, e.g. "It's really hot today"
- unknown: Unable to identify the intent

🔹 menu_scope (used only when intent is `order` or `menu_info`):
- general: General menu inquiry, e.g. "What's recommended?", "Can I see the menu?"
- category: Asking about a specific category, e.g. "What drinks do you have?", "Any desserts?"
- specific: Asking about a specific item, e.g. "Do you have crab fried rice?", "One bubble milk tea please"
- n/a: Not related to menu

If unsure, choose menu_scope = "general"

Please respond only in the following JSON format:  
Do not create new intent or menu_scope names  
Do not add any explanations or text outside of the JSON

### Example:
{{
  "intent": "menu_info",
  "confidence": 0.86,
  "menu_scope": "specific"
}}

User message:
"{user_input}"
""".strip()

    
    def build_prompt_by_intent(self, coarse_intent: str, user_input: str, order_list=None, menu_scope: str = "general") -> str:
        # Coarse intent categories:
        # greeting → build_light_prompt
        # call_staff → build_light_prompt
        # request_bill → build_light_prompt
        # social → build_light_prompt
        # order → build_order_prompt
        # menu_info → build_info_prompt
        # promotion → build_info_prompt
        # unknown → build_user_prompt
        logger.debug(f"build_prompt_by_intent - coarse_intent: #{coarse_intent}#")
        if coarse_intent in ["greeting", "call_staff", "request_bill", "social"]:
            return self.build_light_prompt(user_input)
        elif coarse_intent == "order":
            return self.build_order_prompt(user_input, order_list)
        elif coarse_intent in ["menu_info", "promotion"]:
            if menu_scope in ["category", "specific"]:
                return self.build_info_prompt(user_input, full_menu=True)
            else:
                return self.build_info_prompt(user_input, full_menu=False)
        elif coarse_intent == "unknown":
            return self.build_user_prompt(user_input, order_list)
        else:
            return self.build_user_prompt(user_input, order_list)

    def build_light_prompt(self, user_input: str) -> str:
        return f"""
User: {user_input}

Please respond with the appropriate intent in JSON format only.

- Do not create new intent names  
- Do not include any explanatory text outside the JSON  
- Do not wrap the JSON with ``` or ```json  
""".strip()
    
    def build_order_prompt(self, user_input: str, order_list=None) -> str:
        logger.debug("Enter build_order_prompt")
        order_text = ""
        if order_list:
            aggregated = self.aggregate_order_json(order_list)
            logger.debug(f"build_order_prompt aggregated: {aggregated}")
            if aggregated:
                order_text = "\n\nรายการที่ลูกค้าสั่งแล้ว:\n" + "\n".join(
                    [f"- {item['name']} x {item['qty']} ({item['price']} บาท)" for item in aggregated]
                )
        menu_items = json.dumps(self.get_menu_items(with_price=True, as_json=True), ensure_ascii=False, indent=2)
        promo_text = self.get_promotion_text()

        return f"""
User said: {user_input}

{order_text}

### Full Menu (only select from these items):
{menu_items}

### Promotions:
{promo_text}

### Instructions:
- You are an AI assistant in a restaurant. Your task is to help customers order food and drinks from the provided menu.
- Your response must follow the JSON format shown below and be suitable for both display and spoken output.
- You should calculate total price and apply relevant discounts from the promotion list if applicable.
- Only use the fields exactly as shown in the example. Do not invent or add any other field (e.g., do not use `removed_item`, `updated_item`, etc).
- Use only `"item"` for all intents that modify the order.
- For `add_order`, increase quantity if item exists. For `modify_order`, `qty` means the new final quantity (e.g., 0 = remove, 2 = set to 2).
- Response text must be in Thai with valid SSML for Google Cloud TTS.
- Only include items listed in the menu.
- If an item is not available, inform the user politely in Thai.
- Do not create new intent names or include any explanation outside the JSON.

### Response format (example):
{{
  "intent": "add_order",
  "item": {{ "name": "ข้าวผัดกุ้ง", "qty": 1, "price": 60 }},
  "response": "<speak><prosody rate='110%' pitch='+1st'>รับข้าวผัดกุ้ง 1 ที่นะคะ <break time='300ms'/> เพิ่มอะไรอีกไหมคะ?</prosody></speak>",
  "total_price": 170,
  "discount": 10
}}
""".strip()


    def build_recommendation_prompt(self, user_input: str, order_list=None) -> str:
        logger.debug("Enter build_recommendation_prompt")
        recommendation_text = self._get_recommendations_from_order(order_list)
        return f"""
User: {user_input}

{recommendation_text}
If you detect that there may be additional recommended menu items or if a promotion condition is nearly met,  
please proactively suggest a menu item using intent = proactive_suggestion and respond with a spoken message in SSML format.

Please respond with the appropriate intent in JSON format only.  
- Do not create new intent names  
- Do not include any explanatory text outside the JSON  
""".strip()

    def build_info_prompt(self, user_input: str, full_menu: bool = False) -> str:

        logger.debug("Enter build_info_prompt")
        if full_menu:
            menu_items = json.dumps(self.get_menu_items(with_price=True, as_json=True), ensure_ascii=False, indent=2)
        else:
            menu_items = json.dumps(self.get_menu_items(with_price=True, as_json=True, limit=5), ensure_ascii=False, indent=2)

        # Insert instruction notes as requested
        instruction_notes = """
- Only use the fields exactly as shown in the example. Do not invent or add any other field (e.g., do not use `removed_item`, `updated_item`, etc).
- Use only `"item"` for all intents that modify the order.
- For `add_order`, increase quantity if item exists. For `modify_order`, `qty` means the new final quantity (e.g., 0 = remove, 2 = set to 2).
""".strip()

        promo_text = self.get_promotion_text()  # หรือ self.get_promotion_text(limit=3)

        return f"""
User: {user_input}

### Menu List:
{menu_items}

### Promotions:
{promo_text}

If the user inquires about the menu or promotions, and you find there might be additional recommended items or a promotion condition is nearly fulfilled,  
please proactively suggest menu items using intent = proactive_suggestion and respond with a spoken message in SSML format.

{instruction_notes}

Please respond with the appropriate intent in JSON format only.  
- The intent must be related to providing information (e.g., menu or promotions)  
- Do not create new intent names  
- Do not include any explanatory text outside the JSON  
""".strip()