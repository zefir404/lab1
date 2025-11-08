"""Репозиторий товаров (Inventory) с базовыми CRUD операциями."""
from typing import Dict, Optional, Any
from exceptions.store_exceptions import StoreError, OutOfStockError, InvalidQuantityError
from .product import Product

class Inventory:
    """Управление набором товаров.

    Методы:
        add_product: добавить товар
        find: найти товар по id
        reserve: зарезервировать (уменьшить запас)
        release: вернуть запас
        to_dict / from_dict: сериализация
    """
    def __init__(self) -> None:
        self.products: Dict[str, Product] = {}

    def add_product(self, product: Product) -> None:
        """Добавляет новый товар в инвентарь.

        Raises:
            StoreError: если продукт с таким id уже существует.
        """
        if product.id in self.products:
            raise StoreError(f"Продукт с id {product.id} уже существует")
        self.products[product.id] = product

    def find(self, product_id: str) -> Optional[Product]:
        """Возвращает объект Product по id или None, если не найден."""
        return self.products.get(product_id)

    def update_stock(self, product_id: str, new_stock: int) -> None:
        """Обновляет количество товара на складе (переустановка)."""
        p = self.find(product_id)
        if not p:
            raise StoreError(f"Продукт {product_id} не найден")
        if new_stock < 0:
            raise InvalidQuantityError("stock не может быть отрицательным")
        p.stock = new_stock

    def reserve(self, product_id: str, qty: int) -> None:
        """Резервирует qty единиц товара (уменьшает stock).

        Raises:
            InvalidQuantityError: если qty <= 0
            StoreError: если товар не найден
            OutOfStockError: если недостаточно на складе
        """
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть > 0")
        p = self.find(product_id)
        if not p:
            raise StoreError(f"Продукт {product_id} не найден")
        if p.stock < qty:
            raise OutOfStockError(f"На складе {p.stock}, требуется {qty}")
        p.change_stock(-qty)

    def release(self, product_id: str, qty: int) -> None:
        """Возвращает в запас ранее зарезервированные qty единиц."""
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть > 0")
        p = self.find(product_id)
        if not p:
            raise StoreError(f"Продукт {product_id} не найден")
        p.change_stock(qty)

    def to_dict(self) -> Dict[str, Any]:
        return {"products": [p.to_dict() for p in self.products.values()]}

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.products.clear()
        for p in data.get("products", []):
            prod = Product(**p)
            self.products[prod.id] = prod
