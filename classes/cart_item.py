from dataclasses import dataclass, asdict

@dataclass
class CartItem:
    product_id: str
    quantity: int

    def to_dict(self):
        return asdict(self)
