class SessionManager:
    def __init__(self):
        self.sessions = {}

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
        system_prompt = session.get("system_prompt", "")
        history = session.get("history", [])
        messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        messages.extend(history)
        return messages

    def add_user_message(self, session_id, message):
        self.sessions[session_id]["history"].append({"role": "user", "content": message})
        self.sessions[session_id]["fresh"] = False

    def add_assistant_reply(self, session_id, message):
        self.sessions[session_id]["history"].append({"role": "assistant", "content": message})
        self.sessions[session_id]["fresh"] = False

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

    def update_order_status(self, session_id, item_name, new_status):
        for item in self.sessions[session_id]["orders"]:
            if getattr(item, "name", None) == item_name:
                item.status = new_status
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
    

    def summarize_if_needed(self, session_id):
        history = self.sessions.get(session_id, {}).get("history", [])
        total_characters = sum(len(msg["content"]) for msg in history if msg["role"] != "system")
        if len(history) > 10 or total_characters > 3000:
            summary_text = self.get_summarized_history(session_id, history)
            self.sessions[session_id]["summary_text"] = summary_text
            self.sessions[session_id]["history"] = []

    def get_summarized_history(self, session_id, history):
        from server.mira.services.gpt_client import gpt_summarize
        import re
        messages_to_summarize = [
            {"role": msg["role"], "content": re.sub(r"<[^>]+>", "", msg["content"])}
            for msg in history if msg["role"] != "system"
        ]
        previous_summary = self.sessions[session_id].get("summary_text", "")
        if previous_summary:
            messages_to_summarize.insert(0, {"role": "system", "content": previous_summary})
        summary = gpt_summarize(messages_to_summarize)
        return summary

    def get_summary_text(self, session_id):
        return self.sessions.get(session_id, {}).get("summary_text", "")
    
    # Create a singleton instance for import
session_manager = SessionManager()