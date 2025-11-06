from dataclasses import dataclass
from exceptions.store_exceptions import PaymentError

@dataclass
class Payment:
    id: str
    order_id: str
    amount: float
    method: str
    status: str = "pending"

    def process(self):
        if self.amount <= 0:
            self.status = "failed"
            raise PaymentError("Сумма платежа должна быть > 0")
        self.status = "completed"
        return True
