"""Позиция в корзине."""
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class CartItem:
    product_id: str
    quantity: int

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает словарь для сериализации позиции корзины."""
        return asdict(self)
