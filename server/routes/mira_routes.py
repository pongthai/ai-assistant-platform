# server/routes/mira_routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "MIRA API is running."}