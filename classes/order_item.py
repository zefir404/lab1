"""Модуль обработки платежей (симуляция)."""
from dataclasses import dataclass
from typing import Dict, Any
from exceptions.store_exceptions import PaymentError

@dataclass
class Payment:
    id: str
    order_id: str
    amount: float
    method: str
    status: str = "pending"

    def process(self) -> bool:
        """Обрабатывает платёж. Возвращает True при успехе.

        В реальной системе здесь был бы вызов платежного шлюза.
        Для демонстрации: сумма > 0 => успех, иначе — ошибка.

        Raises:
            PaymentError: если amount <= 0
        """
        if self.amount <= 0:
            self.status = "failed"
            raise PaymentError("Сумма платежа должна быть > 0")
        self.status = "completed"
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status
        }
