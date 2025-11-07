"""Вспомогательные функции проекта."""
import uuid

def generate_id(prefix: str = "") -> str:
    """Генерирует короткий уникальный идентификатор с необязательным префиксом.

    Args:
        prefix: строковый префикс, например 'o' для orders

    Returns:
        Строка идентификатора.
    """
    return f"{prefix}{uuid.uuid4().hex[:8]}"
