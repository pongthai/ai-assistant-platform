from typing import Optional, List
from pydantic import BaseModel


class OrderItem(BaseModel):
    qty: int
    name: str
    status: str
    price: Optional[float] = None
    discount_price: Optional[float] = None


class AssistantResponse(BaseModel):
    intent: str
    response_ssml: Optional[str] = None
    orders: Optional[List[OrderItem]] = None
    total_price: Optional[str] = None
    discount: Optional[str] = None

def build_response(intent: str, ssml_text: str) -> AssistantResponse:
    return AssistantResponse(intent=intent, response_ssml=ssml_text)
