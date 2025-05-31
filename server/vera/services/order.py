from dataclasses import dataclass
from typing import Optional

@dataclass
class OrderItem:
    name: str
    qty: int = 1
    price: Optional[float] = None
    note: Optional[str] = None

    def total(self) -> float:
        return (self.price or 0) * self.qty