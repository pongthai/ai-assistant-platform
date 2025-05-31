# server/routers/vera_routes.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class VERAChatRequest(BaseModel):
    session_id: str
    user_input: str


@router.get("/")
async def root():
    return {"message": "VERA API is running."}

@router.post("/chat")
async def handle_vera_chat(req: VERAChatRequest):
    return {"reply": f"คุณพูดว่า: {req.user_input}"}