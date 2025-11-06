from dataclasses import dataclass, asdict

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: float

    def subtotal(self) -> float:
        return self.quantity * self.price

    def to_dict(self):
        return asdict(self)
