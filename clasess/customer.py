from __future__ import annotations
from typing import List, Optional
from clasess.order import Order

class Customer:
    """Класс для представления покупателя интернет-магазина."""
    def __init__(self, email: str, name: str, balance: float = 0.0):
        self.email: str = email
        self.name: str = name
        self.balance: float = balance
        self.orders: List[Order] = []

    def can_afford(self, amount: float) -> bool:
        """Проверяет, хватает ли денег на покупку."""
        return self.balance >= amount

    def pay(self, amount: float) -> bool:
        """Списывает средства, если хватает баланса."""
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

    def add_order(self, order: Order) -> None:
        """Добавляет заказ в список покупателя."""
        self.orders.append(order)

    def __repr__(self) -> str:
        return f"<Customer {self.name} ({self.email}), balance={self.balance:.2f}>"
