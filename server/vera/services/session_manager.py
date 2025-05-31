from collections import defaultdict
from core.utils.logger_config import get_logger
from server.vera.services.order import OrderItem
from typing import List, Dict, Optional
from server.vera.services.gpt_client import ask_gpt

logger = get_logger(__name__)

class SessionManager:
    def __init__(self, max_history=30):
        self.sessions: Dict[str, Dict] = {}
        self.max_history = max_history

    def init_session(self, session_id: str, system_prompt: str):
        self.sessions[session_id] = {
            "messages": [{"role": "system", "content": system_prompt}],
            "order_list": []
        }
        logger.info(f"🆕 Session initialized: {session_id}")

    def get_history(self, session_id: str):
        messages = self.sessions[session_id]["messages"]
        if len(messages) > self.max_history:
            logger.info(f"🧠 Summarizing session: {session_id} ({len(messages)} messages)")
            summary_prompt = [
                {"role": "system", "content": "กรุณาสรุปสาระสำคัญของบทสนทนาให้กระชับในรูปแบบที่ GPT สามารถเข้าใจและตอบต่อได้ โดยไม่ต้องอธิบายบริบทเพิ่มเติม"},
                *messages
            ]
            summary_text = ask_gpt(summary_prompt)
            logger.info(f"📝 Summary: {summary_text[:60]}...")
            # Replace all history with 1 summarized message
            self.sessions[session_id]["messages"] = [
                {"role": "system", "content": summary_text}
            ]
        return self.sessions[session_id]["messages"]

    def add_user_message(self, session_id: str, text: str):
        self.sessions[session_id]["messages"].append({"role": "user", "content": text})

    def add_assistant_reply(self, session_id: str, text: str):
        self.sessions[session_id]["messages"].append({"role": "assistant", "content": text})

    def reset_session(self, session_id: str):
        logger.info(f"🔄 Resetting session: {session_id}")
        if session_id in self.sessions:
            del self.sessions[session_id]

    def has_session(self, session_id: str) -> bool:
        return session_id in self.sessions

    def get_order_list(self, session_id: str) -> List[OrderItem]:
        return self.sessions[session_id].get("order_list", [])

    def add_order_item(self, session_id: str, item: OrderItem):
        self.sessions[session_id]["order_list"].append(item)

    def clear_order(self, session_id: str):
        self.sessions[session_id]["order_list"] = []