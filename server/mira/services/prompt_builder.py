from pathlib import Path
import json
from core.utils.logger_config import get_logger
logger = get_logger()

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

        logger.debug(f"menu_items: {menu_items}") 

        return f"""
คุณคือ MIRA ผู้ช่วย AI ประจำโต๊ะอาหาร พูดจาสุภาพ น่าเชื่อถือ และตอบกลับด้วย SSML เท่านั้น
คุณมีหน้าที่แนะนำเมนูตามที่อยู่ในรายการอาหารเท่านั้น และสามารถรับออร์เดอร์ และแจ้งโปรโมชั่น

คุณสามารถให้คำแนะนำเมนูเชิงรุก (proactively suggest) กับลูกค้าได้ เช่น การแนะนำเมนูที่ลูกค้า อาจสนใจและเข้ากันกับเมนูที่ลูกค้าได้สั่งไป หรือเข้าใกล้เงื่อนไขโปรโมชั่น 

รายการ intent ที่ระบบรองรับ:
- greeting: ทักทายลูกค้า
- add_order: เพิ่มเมนูเข้าออเดอร์ใหม่
- cancel_order: ยกเลิกรายการอาหาร
- modify_order: แก้ไขเมนูหรือจำนวน
- show_menu: ขอรายการเมนูทั้งหมด
- show_promotion: ขอทราบโปรโมชั่น
- recommend_dish: ขอคำแนะนำเมนู
- suggest_combo: เสนอเมนูที่เข้าคู่กับรายการที่ลูกค้าสั่งแล้ว
- confirm_order: ยืนยันรายการที่สั่ง
- call_staff: เรียกพนักงาน
- request_bill: ขอเช็คบิล
- payment_method: ถามหรือแจ้งวิธีการจ่ายเงิน
- open_topic: พูดคุยเรื่องทั่วไป
- proactive_suggestion: ข้อเสนอแนะเชิงรุกจากระบบ
- unknown: ไม่สามารถเข้าใจข้อความของผู้ใช้ได้

รายการอาหาร:
{menu_items}

โปรโมชั่นปัจจุบัน:
{promo_text}

ตอบกลับคำถามของลูกค้าในรูปแบบ JSON เท่านั้น โดยไม่ใส่คำอธิบายนอก JSON
ให้ใช้ SSML ครอบด้วย <speak><prosody rate="108%" pitch="+1st">...</prosody></speak> และควรใช้ <break time="300ms"/> เพื่อเว้นจังหวะ

ตัวอย่างการตอบ:
{{
  "intent": "add_order",
  "item": {{ "name": "แกงเขียวหวานไก่", "qty": 1 }},
  "response": "<speak><prosody rate='110%' pitch='+1st'>รับแกงเขียวหวานไก่ 1 ที่ค่ะ <break time='300ms'/> เพิ่มอะไรอีกไหมคะ?</prosody></speak>"
}}

หากไม่มีคำสั่งซื้อ ให้ตอบด้วย intent เช่น greeting, show_promotion, recommend_dish เป็นต้น
หากอยากเสนอเมนูแบบ proactive ให้ใช้ intent = proactive_suggestion
ตอบกลับเฉพาะ JSON เท่านั้น
ห้ามใส่เครื่องหมาย ``` หรือ ```json หรือห่อ JSON ด้วย Markdown code block โดยเด็ดขาด
""".strip()

    def _get_recommendations_from_order(self, order_list):
        if not order_list:
            return ""
        suggested = []
        for item in order_list:
            item_id = item.get("id")
            if not item_id:
                continue
            recs = self.recommendations.get("based_on_order", {}).get(item_id, [])
            for rec in recs:
                suggested.append(f"- {rec['id']}: {rec['reason']}")
        if suggested:
            return "\n\nเมนูแนะนำเพิ่มเติมจากรายการที่สั่ง:\n" + "\n".join(suggested)
        return ""

    def build_user_prompt(self, user_input, order_list=None):
        logger.debug("enter build_user_prompt")
        intent_list = """
        - greeting
        - add_order
        - cancel_order
        - modify_order
        - show_menu
        - show_promotion
        - recommend_dish
        - suggest_combo
        - confirm_order
        - call_staff
        - request_bill
        - payment_method
        - open_topic
        - proactive_suggestion
        - unknown
        """.strip()

        order_text = ""
        if order_list:
            order_text = "\n\nรายการที่ลูกค้าสั่งแล้ว:\n" + "\n".join(
                [f"- {item['name']} x {item.get('qty', 1)}" for item in order_list]
            )
        recommendation_text = self._get_recommendations_from_order(order_list)

        return f"""
ผู้ใช้: {user_input}

โปรดตอบกลับด้วย intent ที่เหมาะสมในรูปแบบ JSON เท่านั้น โดย intent ต้องอยู่ในรายการด้านล่างนี้ ห้ามตั้งชื่อ intent ใหม่โดยเด็ดขาด:
{intent_list}
{order_text}
{recommendation_text}

ห้ามใส่ข้อความบรรยายอื่นนอก JSON
ห้ามใช้เครื่องหมาย ``` หรือ ```json ครอบ JSON โดยเด็ดขาด

ถ้าเป็นข้อความพูด ให้ใช้ SSML ครอบด้วย <speak><prosody rate="110%" pitch="+1st">...</prosody></speak>
และใช้ <break time="300ms"/> เพื่อเว้นจังหวะ

ตัวอย่างที่ถูกต้อง:
{{
  "intent": "greeting",
  "response": "<speak><prosody rate='110%' pitch='+1st'>สวัสดีค่ะ</prosody></speak>"
}}
""".strip()
