from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
from .order_item import OrderItem

@dataclass
class Order:
    id: str
    customer_id: str
    items: List[OrderItem]
    status: str = "created"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def total(self) -> float:
        return sum(i.subtotal() for i in self.items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": [i.to_dict() for i in self.items],
            "status": self.status,
            "created_at": self.created_at,
            "total": self.total()
        }
