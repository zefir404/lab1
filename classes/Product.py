from dataclasses import dataclass, asdict
from exceptions.store_exceptions import OutOfStockError

@dataclass
class Product:
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: str = None

    def to_dict(self):
        return asdict(self)

    def change_stock(self, delta: int):
        if self.stock + delta < 0:
            raise OutOfStockError(f"Недостаточно на складе для товара {self.id}")
        self.stock += delta
