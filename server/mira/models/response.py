from typing import Optional
from pydantic import BaseModel

class AssistantResponse(BaseModel):
    intent: str
    response_ssml: Optional[str] = None

def build_response(intent: str, ssml_text: str) -> AssistantResponse:
    return AssistantResponse(intent=intent, response_ssml=ssml_text)
