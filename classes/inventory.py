from typing import Dict
from exceptions.store_exceptions import StoreError, OutOfStockError, InvalidQuantityError
from .product import Product

class Inventory:
    def __init__(self):
        self.products: Dict[str, Product] = {}

    def add_product(self, product: Product):
        if product.id in self.products:
            raise StoreError(f"Продукт с id {product.id} уже существует")
        self.products[product.id] = product

    def find(self, product_id: str):
        return self.products.get(product_id)

    def reserve(self, product_id: str, qty: int):
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть > 0")
        p = self.find(product_id)
        if not p:
            raise StoreError(f"Продукт {product_id} не найден")
        if p.stock < qty:
            raise OutOfStockError(f"На складе {p.stock}, требуется {qty}")
        p.change_stock(-qty)

    def release(self, product_id: str, qty: int):
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть > 0")
        p = self.find(product_id)
        if not p:
            raise StoreError(f"Продукт {product_id} не найден")
        p.change_stock(qty)

    def to_dict(self):
        return {"products": [p.to_dict() for p in self.products.values()]}

    def from_dict(self, data: dict):
        self.products.clear()
        for p in data.get("products", []):
            prod = Product(**p)
            self.products[prod.id] = prod
