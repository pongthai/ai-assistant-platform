# server/routers/shared_routes.py
from fastapi import APIRouter

router = APIRouter()

 

@router.get("/")
async def root():
    return {"message": "Shared API is running."}

