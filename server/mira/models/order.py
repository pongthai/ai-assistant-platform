# File: server/mira/models/order.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrderStatus(str, Enum):
    new = "new"
    in_progress = "ordered_inprogress"
    delivered = "ordered_delivered"
    canceled = "order_canceled"

class OrderItem(BaseModel):
    id: Optional[str] = None
    name: str
    qty: int = Field(..., gt=0)
    price: float = Field(..., ge=0.0)
    status: OrderStatus = OrderStatus.new
    created_at: datetime = Field(default_factory=datetime.utcnow)
