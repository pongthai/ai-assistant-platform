from pathlib import Path
import json
from server.mira.models.order import OrderStatus

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

    def build_init_prompt(self):
        logger.debug("enter build_init_prompt")
        menu_items = "\n".join(
            [f"- {item['name']} ({item['price']} บาท)" for item in self.menu]
        )
        promo_text = "\n".join([f"- {p}" for p in self.promotions])

        intent_list = """
          🔹 หมวด Action:
          - greeting: ทักทายลูกค้า
          - call_staff: เรียกพนักงาน
          - request_bill: ขอเช็คบิล
          - payment_method: ถามหรือแจ้งวิธีจ่ายเงิน

          🔹 หมวด Order:
          - add_order: เพิ่มเมนูเข้าออร์เดอร์
          - cancel_order: ยกเลิกรายการอาหารทั้งหมดที่ยังไม่ได้ดำเนินการ
          - modify_order: ปรับจำนวนหรือยกเลิกบางรายการ
          - confirm_order: ยืนยันออร์เดอร์เพื่อดำเนินการต่อ

          🔹 หมวด Information:
          - show_menu: ขอรายการเมนูทั้งหมด
          - show_promotion: ขอทราบโปรโมชั่น
          - recommend_dish: ขอคำแนะนำเมนู
          - suggest_combo: เสนอเมนูที่เข้าคู่กับสิ่งที่สั่งแล้ว

          🔹 หมวดอื่น ๆ:
          - proactive_suggestion: ระบบเสนอเมนูเชิงรุก
          - open_topic: พูดคุยเรื่องทั่วไป
          - unknown: ไม่เข้าใจข้อความ
          """.strip()
        

        logger.debug(f"menu_items: {menu_items}") 

        return f"""
          คุณคือ MIRA ผู้ช่วย AI บนโต๊ะอาหาร พูดจาสุภาพ ให้ข้อมูลกระชับ และใช้ SSML ในการตอบเท่านั้น  
          หน้าที่ของคุณ:
          - แนะนำเมนูจากรายการด้านล่าง
          - รับออร์เดอร์
          - แจ้งโปรโมชั่น และเสนอเมนูเชิงรุก
          - ตอบคำถามทั่วไปอย่างเหมาะสม

          รูปแบบการตอบต้องเป็น **JSON เท่านั้น** ห้ามใส่ Markdown หรือข้อความอื่นนอก JSON
          ห้ามใช้ ``` หรือ ```json ครอบข้อความ

          เมื่อเป็นข้อความพูด ให้ใช้ SSML:
          <speak><prosody rate="108%" pitch="+1st">...</prosody></speak> พร้อม <break time="300ms"/>

          ### รายการ intent ที่ระบบรองรับ:
          {intent_list}

          ### คำสั่ง:
          - ห้ามคิดชื่อเมนูใหม่  
          - ชื่อเมนูต้องตรงกับที่ระบุในรายการอาหารเท่านั้น  

          ### ตัวอย่างที่ถูกต้อง:
          {{
            "intent": "add_order",
            "item": {{ "name": "ข้าวผัดกุ้ง", "qty": 1 }},
            "response": "<speak><prosody rate='110%' pitch='+1st'>รับข้าวผัดกุ้ง 1 ที่นะตะ <break time='300ms'/> เพิ่มอะไรอีกไหมคะ?</prosody></speak>"
          }}

          ### รายการอาหาร:
          {menu_items}

          ### โปรโมชั่น:
          {promo_text}

          หมายเหตุ:
          - หากผู้ใช้ถามแบบทั่วไป เช่น "มีอะไรแนะนำบ้าง", "มีเมนูอะไร" ให้ตอบด้วยการ **ยกตัวอย่าง 2–3 เมนู + ชวนเจาะจง**
          - ห้ามตอบเมนูทั้งหมดในคราวเดียว
          - ถ้าตอบเชิงรุก ให้ใช้ intent = proactive_suggestion
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

    @staticmethod
    def aggregate_order(order_list):
        from collections import defaultdict
        counter = defaultdict(int)
        for item in order_list:
            logger.debug(f"aggregate_order : order=[{getattr(item, 'name', None)},  {getattr(item, 'qty', 1)}, {getattr(item, 'status', None)}] ")
            if getattr(item, "status", None) == OrderStatus.canceled:
                continue
            name = getattr(item, "name", None)
            qty = getattr(item, "qty", 1)
            counter[name] += qty
        return [f"- {name} x {qty}" for name, qty in counter.items()]

    def build_user_prompt(self, user_input, order_list=None):
        logger.debug("enter build_user_prompt")

        order_text = ""
        if order_list:
            aggregated = self.aggregate_order(order_list)
            order_text = "\n\nรายการที่ลูกค้าสั่งแล้ว:\n" + "\n".join(aggregated)
        recommendation_text = self._get_recommendations_from_order(order_list)

        return f"""
### บริบท
ผู้ใช้: {user_input}

{order_text}
{recommendation_text}

### คำสั่ง:
โปรดตอบกลับด้วย intent ที่เหมาะสมในรูปแบบ JSON เท่านั้น  
- intent ต้องอยู่ในรายการที่ระบบกำหนดไว้ (ตาม system prompt)  
- ห้ามตั้งชื่อ intent ใหม่  
- ห้ามใส่คำบรรยายอื่นนอก JSON  
- ห้ามใช้ ``` หรือ ```json ครอบ JSON  
- หากพบโอกาสเสนอเมนูเพิ่มเติม เช่น เมนูที่เข้าคู่กับรายการที่สั่ง หรือใกล้ครบเงื่อนไขโปรโมชั่น ให้ใช้ intent = proactive_suggestion

### รูปแบบการพูด:
หากเป็นข้อความพูด ให้ใช้:
<speak><prosody rate="110%" pitch="+1st">...</prosody></speak>  
พร้อม <break time="300ms"/> เพื่อเว้นจังหวะ

### ตัวอย่างที่ถูกต้อง:
{{
  "intent": "greeting",
  "response": "<speak><prosody rate='110%' pitch='+1st'>สวัสดีค่ะ</prosody></speak>"
}}
""".strip()