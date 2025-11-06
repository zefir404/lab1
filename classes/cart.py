from dataclasses import dataclass, field
from typing import Dict, Optional
from exceptions.store_exceptions import InvalidQuantityError
from .cart_item import CartItem

@dataclass
class Cart:
    owner_id: str
    items: Dict[str, CartItem] = field(default_factory=dict)

    def add(self, product_id: str, quantity: int = 1):
        if quantity <= 0:
            raise InvalidQuantityError("Количество должно быть > 0")
        if product_id in self.items:
            self.items[product_id].quantity += quantity
        else:
            self.items[product_id] = CartItem(product_id=product_id, quantity=quantity)

    def remove(self, product_id: str, quantity: Optional[int] = None):
        if product_id not in self.items:
            return
        if quantity is None or quantity >= self.items[product_id].quantity:
            del self.items[product_id]
        else:
            self.items[product_id].quantity -= quantity

    def to_list(self):
        return [ci.to_dict() for ci in self.items.values()]
