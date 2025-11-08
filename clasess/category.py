"""Модель категории товаров."""
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class Category:
    """Категория товара.

    Attributes:
        id: Уникальный идентификатор.
        name: Название категории.
        description: Описание категории.
    """
    id: str
    name: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сериализации."""
        return asdict(self)
