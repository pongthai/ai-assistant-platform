import asyncio
from collections import defaultdict
from core.utils.logger_config import get_logger
from server.mira.models.order import OrderStatus


logger = get_logger(__name__)

class SessionManager:
    MAX_HISTORY_COUNT = 5
    MAX_HISTORY_CHARACTERS = 3000
    def __init__(self):
        self.sessions = {}
        self.session_locks = defaultdict(asyncio.Lock)

    def init_session(self, session_id, system_prompt=""):
        self.sessions[session_id] = {
            "orders": [],
            "history": [],
            "system_prompt": system_prompt,
            "status": "active",
            "language": "th",
            "fresh": True,
            "summary_text": ""
        }

    def reset_session(self, session_id):
        self.init_session(session_id)

    def has_session(self, session_id):
        return session_id in self.sessions

    # Removed mark_session_initialized (no longer needed)

    def get_history(self, session_id):
        session = self.sessions.get(session_id, {})
        return session.get("history", [])

    def add_user_message(self, session_id, message):
        logger.debug(f"[{session_id}] 👤 User: {message}")
    
        if session_id not in self.sessions:
            self.sessions[session_id] = {"history": []}  # หรือ preload ค่าอื่นๆ ถ้าต้องใช้
        self.sessions[session_id]["history"].append({"role": "user", "content": message})
        self.sessions[session_id]["fresh"] = False

    def add_assistant_reply(self, session_id, message):
        logger.debug(f"[{session_id}] 🤖 Assistant: {message}")
        self.sessions[session_id]["history"].append({"role": "assistant", "content": message})
        self.sessions[session_id]["fresh"] = False

    def add_interaction(self, session_id, user_message, assistant_message):
        self.add_user_message(session_id, user_message)
        self.add_assistant_reply(session_id, assistant_message)

    def add_order_item(self, session_id, item):
        self.sessions[session_id]["orders"].append(item)
        self.sessions[session_id]["fresh"] = False

    def get_order_list(self, session_id, status_filter=None):
        orders = self.sessions[session_id]["orders"]
        if status_filter:
            return [o for o in orders if getattr(o, "status", None) == status_filter]
        return orders

    def clear_orders(self, session_id):
        self.sessions[session_id]["orders"] = []
        self.sessions[session_id]["fresh"] = False

    def remove_order_item(self, session_id, item_name):
        if session_id in self.sessions:
            for order in self.sessions[session_id]["orders"]:
                if getattr(order, "name", None) == item_name:
                    order.status = OrderStatus.canceled
            self.sessions[session_id]["fresh"] = False

    def update_order_item(self, session_id, item):
        for order in self.sessions[session_id]["orders"]:
            if  getattr(order, "name", None) == getattr(item, "name", None):
                order.status = item.status
                order.qty = item.qty
                order.price = item.price           
                self.sessions[session_id]["fresh"] = False

    def get_order_summary(self, session_id):
        summary = {}
        for o in self.sessions[session_id]["orders"]:
            key = getattr(o, "name", None)
            if key in summary:
                summary[key]["qty"] += getattr(o, "qty", 0)
            else:
                summary[key] = {"qty": getattr(o, "qty", 0), "price": getattr(o, "price", 0)}
        return summary

    def set_language(self, session_id, lang_code):
        self.sessions[session_id]["language"] = lang_code
        self.sessions[session_id]["fresh"] = False

    def get_language(self, session_id):
        return self.sessions[session_id].get("language", "th")

    def set_status(self, session_id, status):
        self.sessions[session_id]["status"] = status
        self.sessions[session_id]["fresh"] = False

    def get_status(self, session_id):
        return self.sessions[session_id]["status"]

    def is_fresh(self, session_id):
        return self.sessions.get(session_id, {}).get("fresh", False)

    def has_history(self, session_id):
        return bool(self.sessions.get(session_id, {}).get("history"))

    def get_system_prompt(self, session_id):
        return self.sessions.get(session_id, {}).get("system_prompt", "")
    

    async def summarize_if_needed(self, session_id):
        async with self.session_locks[session_id]:
            history = self.sessions.get(session_id, {}).get("history", [])
            total_characters = sum(len(msg["content"]) for msg in history if msg["role"] != "system")
            if len(history) > self.MAX_HISTORY_COUNT or total_characters > self.MAX_HISTORY_CHARACTERS:
                summary_text = await self._summarize_history(session_id, history)
                self.sessions[session_id]["summary_text"] = summary_text
                self.sessions[session_id]["history"] = []

    async def _summarize_history(self, session_id, history):        
        from server.mira.services.gpt_client import gpt_summarize
        import re
        logger.debug(f"enter _summarize_history")
        combined_texts = []
        for msg in history:
            if msg["role"] == "system":
                continue
            content = msg.get("content", "")
            if isinstance(content, list):
                text = " ".join(part.get("text", "") for part in content if isinstance(part, dict))
            else:
                text = content
            cleaned_text = re.sub(r"<[^>]+>", "", text)
            combined_texts.append(cleaned_text)

        previous_summary = self.sessions[session_id].get("summary_text", "")
        if previous_summary:
            combined_texts.insert(0, previous_summary)

        full_text = "\n".join(combined_texts)
        summary = await gpt_summarize(full_text)
        return summary

    def get_summary_text(self, session_id):
        return self.sessions.get(session_id, {}).get("summary_text", "")
    
    async def get_full_context(self, session_id, max_history: int = None):
        async with self.session_locks[session_id]:
            context = []
            if self.sessions[session_id].get("system_prompt"):
                context.append({"role": "system", "content": self.sessions[session_id]["system_prompt"]})
            if self.sessions[session_id].get("summary_text"):
                context.append({"role": "system", "content": self.sessions[session_id]["summary_text"]})
            history = self.sessions[session_id].get("history", []).copy()
            if max_history is not None:
                history = history[-max_history:]
            context += history
            return context

    # Create a singleton instance for import
session_manager = SessionManager()