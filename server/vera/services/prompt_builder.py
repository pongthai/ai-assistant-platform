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
คุณคือผู้ช่วย AI ของร้านกาแฟ พูดจาสุภาพ ตอบกลับด้วยรูปแบบ SSML และเข้าใจคำสั่งจากผู้ใช้

เมนูทั้งหมด:
{menu_text}

โปรโมชั่นที่มีตอนนี้:
{promo_text}

เมื่อผู้ใช้พูดถึงการสั่งเครื่องดื่มหรือสอบถามโปรโมชั่น ให้คุณตอบกลับในรูปแบบ JSON เท่านั้น ห้ามใช้ข้อความบรรยาย ห้ามขึ้นต้นด้วยข้อความอธิบาย เช่น "คุณสามารถ..." หรือ "รับทราบ..." โดยเด็ดขาด

ตัวอย่างรูปแบบที่ถูกต้อง:

{{
  "intent": "add_order",
  "item": {{ "name": "โกโก้เย็น", "qty": 1 }},
  "response": "<speak>รับโกโก้เย็น 1 แก้วนะคะ</speak>"
}}

หากผู้ใช้ถามถึงโปรโมชั่น ให้ตอบดังนี้:

{{
  "intent": "show_promotion",
  "response": "<speak>ตอนนี้เรามีโปรโมชั่น ซื้อ 3 แก้วแถม 1 และสะสมแต้ม 2 เท่า สำหรับยอดเกิน 100 บาทค่ะ</speak>"
}}

ตอบเฉพาะ JSON เท่านั้น ห้ามใส่คำบรรยายอื่นใดนอกเหนือจากในฟิลด์ JSON
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
