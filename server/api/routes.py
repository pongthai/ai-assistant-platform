from fastapi import APIRouter, Request
from server.logic.chat_handler import handle_chat

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    return await handle_chat(body)
