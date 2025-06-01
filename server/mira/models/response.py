from pydantic import BaseModel

class AssistantResponse(BaseModel):
    intent: str
    response_ssml: str

def build_response(intent: str, ssml_text: str) -> AssistantResponse:
    return AssistantResponse(intent=intent, response_ssml=ssml_text)

def create_response(intent: str, response: str) -> dict:
    return {
        "intent": intent,
        "response": response
    }
