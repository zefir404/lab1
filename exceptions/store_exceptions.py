"""Модуль пользовательских исключений для интернет-магазина."""
from typing import NoReturn

class StoreError(Exception):
    """Базовый класс всех ошибок магазина."""
    pass

class OutOfStockError(StoreError):
    """Ошибка, когда запрошено больше единиц товара, чем доступно на складе."""
    pass

class InvalidQuantityError(StoreError):
    """Ошибка некорректного количества (например, <= 0)."""
    pass

class PaymentError(StoreError):
    """Ошибка при обработке платежа."""
    pass

class SerializationError(StoreError):
    """Ошибка при сериализации/десериализации данных."""
    pass
