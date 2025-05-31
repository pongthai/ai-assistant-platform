from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union, Dict, Any
from server.shared.gpt_integration import GPTClient
from server.shared.flow_handlers.intent_router import IntentRouter
from server.shared.intent_classifier.classifier import IntentClassifier
from server.shared.session_manager import session_manager

router = APIRouter()
gpt_client = GPTClient()
intent_classifier = IntentClassifier()
intent_router_instance = IntentRouter(gpt_client=gpt_client, intent_classifier=intent_classifier)

class ChatRequest(BaseModel):
    session_id: str
    user_voice: str

class ChatResponse(BaseModel):
    response: Union[str, Dict[str, Any]]

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_input: ChatRequest):
    session_id = chat_input.session_id    
    session = session_manager.get_session(session_id)
    
    state_info = session_manager.get_state_info(session_id)
    if state_info and state_info.get("state") and state_info.get("state") != "complete":
        result = intent_router_instance.route_by_state(state_info["state"], chat_input.user_voice, session)
    else:
        result = intent_router_instance.route(chat_input.user_voice, session)

    session_manager.update_session(session_id, intent=session.intent, state=session.state, context_update=session.context)

    return ChatResponse(response=result)