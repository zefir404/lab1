"""Позиция в заказе (в момент оформления фиксируется цена)."""
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: float

    def subtotal(self) -> float:
        """Возвращает стоимость позиции (quantity * price)."""
        return self.quantity * self.price

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
