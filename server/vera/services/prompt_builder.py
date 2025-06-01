class PromptBuilder:
    def __init__(self, menu_data, promotions):
        self.menu_data = menu_data
        self.promotions = promotions

    def build_init_prompt(self):
        menu_text = "\n".join([
            f"- {item['name']} ({item['price']} บาท)"
            for item in self.menu_data
        ])

        promo_text = "\n".join([
            f"- {promo['title']}"
            for promo in self.promotions
        ])

        prompt = f"""
        คุณคือผู้ช่วย AI ของร้านกาแฟที่พูดจาสุภาพและมีน้ำเสียงเป็นมิตร  
        ให้ตอบกลับในรูปแบบ **JSON เท่านั้น** โดยข้อความในฟิลด์ `response` ต้องอยู่ในรูปแบบ **SSML** และมีโครงสร้างดังนี้:

        - ใช้ `<speak>` ครอบทุกข้อความ
        - ใช้ `<prosody rate="100%" pitch="+1.5st">...</prosody>` ครอบข้อความหลักเพื่อควบคุมโทนเสียง
        - สามารถแทรก `<break time="300ms"/>` เพื่อเว้นจังหวะเมื่อเหมาะสม
        - ห้ามใส่ข้อความบรรยายใด ๆ นอกเหนือจากภายใน JSON
        - ห้ามขึ้นต้นด้วยประโยคอธิบาย เช่น "คุณสามารถ..." หรือ "รับทราบแล้ว..." โดยเด็ดขาด

        เมนูทั้งหมดที่มีให้บริการ:
        {menu_text}

        โปรโมชั่นที่กำลังจัดอยู่ตอนนี้:
        {promo_text}

        เมื่อผู้ใช้:
        - สั่งเครื่องดื่ม: ให้ตอบด้วย `intent = "add_order"` และแสดงชื่อ+จำนวนใน `item`
        - ถามถึงโปรโมชั่น: ให้ตอบด้วย `intent = "show_promotion"`

        **ตัวอย่างที่ถูกต้อง:**
        {{
          "intent": "add_order",
          "item": {{ "name": "โกโก้เย็น", "qty": 1 }},
          "response": "<speak><prosody rate='108%' pitch='+1st'>รับโกโก้เย็น 1 แก้วนะคะ</prosody></speak>"
        }}
    """
        return prompt.strip()

    def build_user_prompt(self, user_text):
        return user_text.strip()

    def build_order_summary_prompt(self, order_list):
        summary_lines = []
        total = 0
        for item in order_list:
            name = item.name
            qty = item.qty
            price = item.price or 0
            subtotal = qty * price
            total += subtotal
            summary_lines.append(f"- {name} {qty} แก้ว (รวม {subtotal} บาท)")

        summary_text = "\n".join(summary_lines)

        prompt = f"""
ลูกค้าสั่ง:
{summary_text}

รวมทั้งหมด {total} บาท

กรุณาช่วยสรุปรายการทั้งหมดอย่างสุภาพในรูปแบบ SSML และสอบถามเพื่อยืนยันก่อนดำเนินการต่อ
ตอบเป็น JSON ดังตัวอย่าง:

{{
  "intent": "confirm_order",
  "response": "<speak>คุณลูกค้าสั่งลาเต้ 2 แก้ว และโกโก้ 1 แก้ว รวม 145 บาท ถูกต้องไหมคะ?</speak>"
}}
"""
        return prompt.strip()

    def build_cancel_prompt(self):
        return """
ลูกค้าต้องการยกเลิกรายการทั้งหมด กรุณาตอบกลับด้วยความสุภาพในรูปแบบ SSML และระบุ intent ว่า "cancel_order"

ตัวอย่างการตอบ:
{
  "intent": "cancel_order",
  "response": "<speak>ไม่เป็นไรค่ะ ยกเลิกรายการให้แล้วนะคะ</speak>"
}
""".strip()

    def build_greeting_prompt(self):
        return """
เริ่มต้นการสนทนากับลูกค้าใหม่ กรุณาทักทายด้วยความสุภาพในรูปแบบ SSML และระบุ intent ว่า "greeting"

ตัวอย่างการตอบ:
{
  "intent": "greeting",
  "response": "<speak>สวัสดีค่ะ ยินดีต้อนรับสู่ร้านเวร่านะคะ รับอะไรดีคะ?</speak>"
}
""".strip()
