"""Интерактивная точка входа для интернет-магазина электроники."""
from typing import List, Optional
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from clasess.inventory import Inventory
from clasess.product import Product
from clasess.order_item import OrderItem
from clasess.order import Order
from clasess.customer import Customer
from clasess.supplier import Supplier
from utils.helpers import generate_id
from exceptions.store_exceptions import StoreError, SerializationError

# ---------------------- Глобальные данные ----------------------
inventory: Inventory = Inventory()
customers: List[Customer] = []
suppliers: List[Supplier] = []
orders: List[Order] = []

JSON_FILE = "data.json"
XML_FILE = "data.xml"

# ---------------------- Вспомогательные функции ----------------------
def find_product_by_id(pid: str) -> Optional[Product]:
    return inventory.find(pid)


def find_customer_by_email(email: str) -> Optional[Customer]:
    return next((c for c in customers if c.email == email), None)


# ---------------------- Загрузка / сохранение ----------------------
def load_from_json() -> None:
    global inventory, customers, suppliers, orders
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        inventory = Inventory()
        customers = []
        suppliers = []
        orders = []
        return

    inventory = Inventory()
    inventory.from_dict(data.get("inventory", {"products": []}))

    customers = [
        Customer(c["email"], c["name"], c.get("balance", 0.0))
        for c in data.get("customers", [])
    ]
    suppliers = [
        Supplier(s["name"], s["contact"])
        for s in data.get("suppliers", [])
    ]

    orders = []
    for o in data.get("orders", []):
        items = [OrderItem(i["product_id"], i["quantity"], i["price"]) for i in o["items"]]
        orders.append(
            Order(
                id=o["id"],
                customer_id=o["customer_id"],
                items=items,
                status=o.get("status", "created"),
                created_at=o.get("created_at", datetime.utcnow().isoformat())
            )
        )


def save_to_json() -> None:
    data = {
        "inventory": inventory.to_dict(),
        "customers": [
            {"email": c.email, "name": c.name, "balance": c.balance} for c in customers
        ],
        "suppliers": [
            {"name": s.name, "contact": s.contact} for s in suppliers
        ],
        "orders": [
            {
                "id": o.id,
                "customer_id": o.customer_id,
                "items": [
                    {"product_id": it.product_id, "quantity": it.quantity, "price": it.price}
                    for it in o.items
                ],
                "status": o.status,
                "created_at": o.created_at
            } for o in orders
        ]
    }
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_to_xml() -> None:
    root = ET.Element("StoreData")

    inv_el = ET.SubElement(root, "Inventory")
    prods_el = ET.SubElement(inv_el, "Products")
    for p in inventory.products.values():
        p_el = ET.SubElement(prods_el, "Product", {"id": p.id})
        ET.SubElement(p_el, "Name").text = p.name
        ET.SubElement(p_el, "Description").text = p.description
        ET.SubElement(p_el, "Price").text = str(p.price)
        ET.SubElement(p_el, "Stock").text = str(p.stock)
        ET.SubElement(p_el, "Category").text = p.category or ""

    custs_el = ET.SubElement(root, "Customers")
    for c in customers:
        c_el = ET.SubElement(custs_el, "Customer")
        ET.SubElement(c_el, "Email").text = c.email
        ET.SubElement(c_el, "Name").text = c.name
        ET.SubElement(c_el, "Balance").text = str(c.balance)

    sups_el = ET.SubElement(root, "Suppliers")
    for s in suppliers:
        s_el = ET.SubElement(sups_el, "Supplier")
        ET.SubElement(s_el, "Name").text = s.name
        ET.SubElement(s_el, "Contact").text = s.contact

    orders_el = ET.SubElement(root, "Orders")
    for o in orders:
        o_el = ET.SubElement(orders_el, "Order")
        ET.SubElement(o_el, "Id").text = o.id
        ET.SubElement(o_el, "CustomerEmail").text = o.customer_id
        items_el = ET.SubElement(o_el, "Items")
        for it in o.items:
            it_el = ET.SubElement(items_el, "Item")
            ET.SubElement(it_el, "ProductId").text = it.product_id
            ET.SubElement(it_el, "Quantity").text = str(it.quantity)
            ET.SubElement(it_el, "Price").text = str(it.price)
        ET.SubElement(o_el, "CreatedAt").text = o.created_at

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

# ---------------------- Меню ----------------------
def customer_menu(customer: Customer) -> None:
    while True:
        print(f"\n=== Личный кабинет {customer.name} ({customer.email}) ===")
        print("1. Просмотреть каталог")
        print("2. Купить товар")
        print("3. Просмотреть мои заказы")
        print("0. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            for p in inventory.products.values():
                print(f"{p.id}: {p.name} ({p.category}) — {p.price}₽, в наличии {p.stock}")

        elif choice == "2":
            pid = input("Введите ID товара: ").strip()
            qty = int(input("Количество: ").strip())
            prod = find_product_by_id(pid)
            if not prod:
                print("Товар не найден.")
                continue
            if prod.stock < qty:
                print("Недостаточно на складе.")
                continue
            total = prod.price * qty
            if not customer.can_afford(total):
                print("Недостаточно средств.")
                continue
            try:
                inventory.reserve(prod.id, qty)
            except StoreError as e:
                print(f"Ошибка: {e}")
                continue
            order = Order(generate_id("o"), customer.email, [OrderItem(prod.id, qty, prod.price)])
            orders.append(order)
            customer.pay(total)
            customer.add_order(order)
            print(f"✅ Заказ оформлен на сумму {total}₽. Номер: {order.id}")

        elif choice == "3":
            if not customer.orders:
                print("У вас нет заказов.")
            else:
                for o in customer.orders:
                    items_str = ", ".join([f"{it.product_id} x{it.quantity}" for it in o.items])
                    print(f"- {o.created_at}: {items_str} | Статус: {o.status}")

        elif choice == "0":
            break
        else:
            print("Неверный выбор.")


def manager_menu() -> None:
    while True:
        print("\n=== Панель менеджера ===")
        print("1. Просмотреть все товары")
        print("2. Добавить товар")
        print("3. Изменить цену/остаток")
        print("4. Удалить товар")
        print("5. Просмотреть заказы")
        print("6. Добавить поставщика")
        print("7. Заказать поставку товара")
        print("0. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            for p in inventory.products.values():
                print(f"{p.id}: {p.name} ({p.category}) — {p.price}₽, {p.stock} шт.")

        elif choice == "2":
            pid = input("ID: ").strip()
            name = input("Название: ").strip()
            desc = input("Описание: ").strip()
            cat = input("Категория: ").strip()
            price = float(input("Цена: ").strip())
            stock = int(input("Количество: ").strip())
            inventory.add_product(Product(pid, name, desc, price, stock, cat))
            print("✅ Товар добавлен.")

        elif choice == "3":
            pid = input("ID товара: ").strip()
            prod = find_product_by_id(pid)
            if not prod:
                print("Товар не найден.")
                continue
            prod.price = float(input("Новая цена: ").strip())
            prod.stock = int(input("Новый остаток: ").strip())
            print("✅ Обновлено.")

        elif choice == "4":
            pid = input("ID товара: ").strip()
            if pid in inventory.products:
                del inventory.products[pid]
                print("✅ Удалено.")
            else:
                print("Не найдено.")

        elif choice == "5":
            if not orders:
                print("Нет заказов.")
            for o in orders:
                items_str = ", ".join([f"{it.product_id} x{it.quantity}" for it in o.items])
                print(f"{o.id} | {o.customer_id} | {items_str} | {o.status}")

        elif choice == "6":
            name = input("Название поставщика: ").strip()
            contact = input("Контакт: ").strip()
            suppliers.append(Supplier(name, contact))
            print("✅ Поставщик добавлен.")

        elif choice == "7":
            if not suppliers:
                print("Нет поставщиков.")
                continue
            print("Список поставщиков:")
            for i, s in enumerate(suppliers, 1):
                print(f"{i}. {s.name} ({s.contact})")
            idx = int(input("Выберите: ")) - 1
            supplier = suppliers[idx]
            pid = input("ID товара для пополнения: ").strip()
            qty = int(input("Количество: ").strip())
            prod = find_product_by_id(pid)
            if not prod:
                print("Товар не найден.")
                continue
            supplier.supply_product(prod, qty)
            print(f"✅ Поставка от {supplier.name}: +{qty} шт. {prod.name}")

        elif choice == "0":
            break
        else:
            print("Неверный выбор.")


# ---------------------- Основной цикл ----------------------
def main() -> None:
    print("Выберите формат данных:")
    print("1. JSON")
    print("2. XML")
    choice = input("Ваш выбор: ").strip()
    if choice == "2":
        load_from_json()
    else:
        load_from_json()

    if not customers:
        customers.extend([
            Customer("alice@example.com", "Alice", 1000.0),
            Customer("bob@example.com", "Bob", 500.0),
        ])

    while True:
        print("\n=== Интернет-магазин электроники ===")
        print("1. Войти как менеджер")
        print("2. Войти как покупатель")
        print("0. Сохранить и выйти")
        print("9. Выйти без сохранения")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            if input("Пароль менеджера: ").strip() == "admin":
                manager_menu()
            else:
                print("Неверный пароль.")

        elif choice == "2":
            email = input("Email: ").strip()
            customer = find_customer_by_email(email)
            if customer:
                customer_menu(customer)
            else:
                if input("Пользователь не найден. Зарегистрировать? (y/n): ").lower() == "y":
                    name = input("Имя: ").strip()
                    balance = float(input("Начальный баланс: ").strip())
                    new_cust = Customer(email, name, balance)
                    customers.append(new_cust)
                    print("✅ Зарегистрирован.")
        elif choice == "0":
            save_to_json()
            save_to_xml()
            print("✅ Данные сохранены. До свидания!")
            break
        elif choice == "9":
            print("Выход без сохранения.")
            break
        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
