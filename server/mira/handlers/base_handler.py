# server/mira/handlers/base_handler.py

from abc import ABC, abstractmethod

class BaseIntentHandler(ABC):
    @abstractmethod
    def handle(self, session_id: str, gpt_response: dict) -> dict:
        pass