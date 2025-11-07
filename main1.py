
from typing import Dict, Any, List, Optional, Tuple
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from utils.serializer import save_inventory_json, save_inventory_xml, load_inventory_json, load_inventory_xml
from classes.inventory import Inventory
from classes.product import Product
from classes.order_item import OrderItem
from classes.order import Order
from utils.helpers import generate_id
from exceptions.store_exceptions import StoreError, SerializationError

# Глобальные данные
inventory: Inventory = Inventory()
customers: List[Dict[str, Any]] = []  # {"email", "name", "balance"}
orders: List[Order] = []

JSON_FILE = "data.json"
XML_FILE = "data.xml"


def find_product_by_id(pid: str) -> Optional[Product]:
    return inventory.find(pid)


def find_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
    return next((c for c in customers if c["email"] == email), None)


# ---------- Загрузка / Сохранение ----------

def load_from_json() -> None:
    global inventory, customers, orders
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        inventory = Inventory()
        customers = []
        orders = []
        return
    except Exception as e:
        raise SerializationError(str(e))

    inventory = Inventory()
    inventory.from_dict(data.get("inventory", {"products": []}))
    customers = data.get("customers", [])

    orders = []
    for o in data.get("orders", []):
        items = [OrderItem(product_id=i["product_id"], quantity=i["quantity"], price=i["price"]) for i in o.get("items", [])]
        orders.append(
            Order(
                id=o["id"],
                customer_id=o["customer_id"],
                items=items,
                status=o.get("status", "created"),
                created_at=o.get("created_at", datetime.utcnow().isoformat())
            )
        )


def load_from_xml() -> None:
    global inventory, customers, orders
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except FileNotFoundError:
        inventory = Inventory()
        customers = []
        orders = []
        return
    except Exception as e:
        raise SerializationError(str(e))

    # inventory
    inv = {"products": []}
    for prod_el in root.findall("./Inventory/Products/Product"):
        pid = prod_el.get("id")
        name = prod_el.findtext("Name") or ""
        desc = prod_el.findtext("Description") or ""
        price = float(prod_el.findtext("Price") or 0.0)
        stock = int(prod_el.findtext("Stock") or 0)
        category = prod_el.findtext("Category") or None
        inv["products"].append({
            "id": pid, "name": name, "description": desc,
            "price": price, "stock": stock, "category": category
        })
    inventory = Inventory()
    inventory.from_dict(inv)

    # customers
    customers.clear()
    for c in root.findall("./Customers/Customer"):
        customers.append({
            "email": c.findtext("Email") or "",
            "name": c.findtext("Name") or "",
            "balance": float(c.findtext("Balance") or 0.0)
        })

    # orders
    orders.clear()
    for o in root.findall("./Orders/Order"):
        oid = o.findtext("Id") or generate_id("o")
        cust = o.findtext("CustomerEmail") or ""
        items = []
        for it in o.findall("./Items/Item"):
            pid = it.findtext("ProductId")
            qty = int(it.findtext("Quantity") or 0)
            price = float(it.findtext("Price") or 0.0)
            items.append(OrderItem(product_id=pid, quantity=qty, price=price))
        created_at = o.findtext("CreatedAt") or datetime.utcnow().isoformat()
        orders.append(Order(id=oid, customer_id=cust, items=items, created_at=created_at))


def save_to_json() -> None:
    data = {
        "inventory": inventory.to_dict(),
        "customers": customers,
        "orders": [
            {
                "id": o.id,
                "customer_id": o.customer_id,
                "items": [{"product_id": it.product_id, "quantity": it.quantity, "price": it.price} for it in o.items],
                "status": o.status,
                "created_at": o.created_at
            }
            for o in orders
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
        ET.SubElement(c_el, "Email").text = c.get("email", "")
        ET.SubElement(c_el, "Name").text = c.get("name", "")
        ET.SubElement(c_el, "Balance").text = str(c.get("balance", 0.0))

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


# ---------- Меню ----------

def customer_menu(email: str) -> None:
    customer = find_customer_by_email(email)
    if not customer:
        print("Покупатель не найден.")
        return

    while True:
        print(f"\n=== Личный кабинет: {customer['name']} ({customer['email']}) ===")
        print("1. Просмотреть каталог")
        print("2. Купить товар")
        print("3. Просмотреть мои заказы")
        print("0. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            print("\nКаталог товаров:")
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
            if customer.get("balance", 0.0) < total:
                print("Недостаточно средств.")
                continue
            try:
                inventory.reserve(prod.id, qty)
            except StoreError as e:
                print(f"Ошибка: {e}")
                continue
            order_id = generate_id("o")
            item = OrderItem(product_id=prod.id, quantity=qty, price=prod.price)
            order = Order(id=order_id, customer_id=email, items=[item])
            orders.append(order)
            customer["balance"] -= total
            print(f"✅ Заказ оформлен. Сумма {total}₽. Номер: {order.id}")

        elif choice == "3":
            cust_orders = [o for o in orders if o.customer_id == email]
            if not cust_orders:
                print("У вас нет заказов.")
            else:
                for o in cust_orders:
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
        print("5. Просмотреть все заказы")
        print("0. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            for p in inventory.products.values():
                print(f"{p.id}: {p.name} ({p.category}) — {p.price}₽, в наличии {p.stock}")

        elif choice == "2":
            pid = input("ID: ").strip()
            name = input("Название: ").strip()
            desc = input("Описание: ").strip()
            cat = input("Категория: ").strip()
            price = float(input("Цена: ").strip())
            stock = int(input("Количество: ").strip())
            new_p = Product(id=pid, name=name, description=desc, price=price, stock=stock, category=cat)
            inventory.add_product(new_p)
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
            pid = input("ID товара для удаления: ").strip()
            if pid in inventory.products:
                del inventory.products[pid]
                print("✅ Удалено.")
            else:
                print("Товар не найден.")

        elif choice == "5":
            if not orders:
                print("Нет заказов.")
            else:
                for o in orders:
                    items_str = ", ".join([f"{it.product_id} x{it.quantity}" for it in o.items])
                    print(f"{o.created_at} | {o.customer_id} | {items_str} | Статус: {o.status}")

        elif choice == "0":
            break
        else:
            print("Неверный выбор.")


def main() -> None:
    print("Выберите формат данных:")
    print("1. JSON")
    print("2. XML")
    choice = input("Ваш выбор: ").strip()
    if choice == "2":
        load_from_xml()
    else:
        load_from_json()

    if not customers:
        customers.extend([
            {"email": "alice@example.com", "name": "Alice", "balance": 1000.0},
            {"email": "bob@example.com", "name": "Bob", "balance": 500.0},
        ])

    while True:
        print("\n=== Интернет-магазин электроники ===")
        print("1. Войти как менеджер")
        print("2. Войти как покупатель")
        print("0. Сохранить и выйти")
        print("9. Выйти без сохранения")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            pwd = input("Пароль менеджера: ").strip()
            if pwd == "admin":
                manager_menu()
            else:
                print("Неверный пароль.")
        elif choice == "2":
            email = input("Email: ").strip()
            cust = find_customer_by_email(email)
            if cust:
                customer_menu(email)
            else:
                print("Не найден. Зарегистрироваться? (y/n)")
                if input().strip().lower() == "y":
                    name = input("Имя: ").strip()
                    balance = float(input("Начальный баланс: ").strip())
                    customers.append({"email": email, "name": name, "balance": balance})
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
