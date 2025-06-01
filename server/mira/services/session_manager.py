# File: server/mira/services/session_manager.py

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def init_session(self, session_id, system_prompt=""):
        self.sessions[session_id] = {
            "orders": [],
            "history": [],
            "system_prompt": system_prompt,
            "status": "active",
            "language": "th"
        }

    def reset_session(self, session_id):
        self.init_session(session_id)

    def has_session(self, session_id):
        return session_id in self.sessions

    def get_history(self, session_id):
        return self.sessions[session_id]["history"]

    def add_user_message(self, session_id, message):
        self.sessions[session_id]["history"].append({"role": "user", "content": message})

    def add_assistant_reply(self, session_id, message):
        self.sessions[session_id]["history"].append({"role": "assistant", "content": message})

    def add_order_item(self, session_id, item):
        self.sessions[session_id]["orders"].append(item)

    def get_order_list(self, session_id, status_filter=None):
        orders = self.sessions[session_id]["orders"]
        if status_filter:
            return [o for o in orders if getattr(o, "status", None) == status_filter]
        return orders

    def clear_orders(self, session_id):
        self.sessions[session_id]["orders"] = []

    def update_order_status(self, session_id, item_name, new_status):
        for item in self.sessions[session_id]["orders"]:
            if getattr(item, "name", None) == item_name:
                item.status = new_status

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

    def get_language(self, session_id):
        return self.sessions[session_id].get("language", "th")

    def set_status(self, session_id, status):
        self.sessions[session_id]["status"] = status

    def get_status(self, session_id):
        return self.sessions[session_id]["status"]

# Create a singleton instance for import
session_manager = SessionManager()
