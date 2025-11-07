"""Модель товара."""
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from exceptions.store_exceptions import OutOfStockError

@dataclass
class Product:
    """Представляет товар в магазине.

    Attributes:
        id: Идентификатор товара.
        name: Название.
        description: Текстовое описание.
        price: Цена за единицу.
        stock: Количество на складе.
        category: Идентификатор категории (опционально).
    """
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает словарь, пригодный для JSON/XML сериализации."""
        return asdict(self)

    def change_stock(self, delta: int) -> None:
        """Изменяет количество товара на складе.

        Args:
            delta: положительное или отрицательное число для изменения запаса.

        Raises:
            OutOfStockError: если после изменения запас станет отрицательным.
        """
        if self.stock + delta < 0:
            raise OutOfStockError(f"Недостаточно на складе для товара {self.id}")
        self.stock += delta
