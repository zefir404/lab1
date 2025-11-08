from __future__ import annotations
from typing import List
from clasess.product import Product

class Supplier:
    """Класс, описывающий поставщика."""
    def __init__(self, name: str, contact: str):
        self.name: str = name
        self.contact: str = contact
        self.products_supplied: List[Product] = []

    def supply_product(self, product: Product, quantity: int) -> None:
        """Добавляет товар к списку поставляемых и увеличивает остаток."""
        product.stock += quantity
        if product not in self.products_supplied:
            self.products_supplied.append(product)

    def __repr__(self) -> str:
        return f"<Supplier {self.name}, supplies={len(self.products_supplied)}>"
