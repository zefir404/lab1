"""Модель корзины покупателя."""
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from exceptions.store_exceptions import InvalidQuantityError
from .cart_item import CartItem

@dataclass
class Cart:
    """Корзина содержит набор CartItem, индексированных по product_id."""
    owner_id: str
    items: Dict[str, CartItem] = field(default_factory=dict)

    def add(self, product_id: str, quantity: int = 1) -> None:
        """Добавляет товар в корзину или увеличивает количество.

        Args:
            product_id: идентификатор товара.
            quantity: количество для добавления (должно быть > 0).

        Raises:
            InvalidQuantityError: если quantity <= 0.
        """
        if quantity <= 0:
            raise InvalidQuantityError("Количество должно быть > 0")
        if product_id in self.items:
            self.items[product_id].quantity += quantity
        else:
            self.items[product_id] = CartItem(product_id=product_id, quantity=quantity)

    def remove(self, product_id: str, quantity: Optional[int] = None) -> None:
        """Удаляет или уменьшает количество позиции в корзине.

        If quantity is None — удаляет позицию полностью.
        If quantity >= current quantity — удаляет позицию.
        Else — уменьшает на указанное количество.
        """
        if product_id not in self.items:
            return
        if quantity is None or quantity >= self.items[product_id].quantity:
            del self.items[product_id]
        else:
            self.items[product_id].quantity -= quantity

    def to_list(self) -> List[Dict[str, int]]:
        """Возвращает список словарей с позициями корзины для сериализации."""
        return [ci.to_dict() for ci in self.items.values()]
