"""Сериализация и десериализация инвентаря в JSON и XML."""
import json
import xml.etree.ElementTree as ET
from typing import Dict
from exceptions.store_exceptions import SerializationError
from clasess.inventory import Inventory

def save_inventory_json(inv: Inventory, filepath: str) -> None:
    """Сохраняет Inventory в JSON файл."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(inv.to_dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise SerializationError(str(e))

def load_inventory_json(filepath: str) -> Inventory:
    """Загружает Inventory из JSON файл."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise SerializationError(str(e))
    inv = Inventory()
    inv.from_dict(data)
    return inv

def save_inventory_xml(inv: Inventory, filepath: str) -> None:
    """Сохраняет Inventory в XML файл."""
    try:
        root = ET.Element("store")
        products_el = ET.SubElement(root, "products")
        for p in inv.products.values():
            pe = ET.SubElement(products_el, "product", {"id": p.id})
            for tag, val in [("name", p.name), ("description", p.description),
                             ("price", str(p.price)), ("stock", str(p.stock)),
                             ("category", p.category or "")]:
                el = ET.SubElement(pe, tag)
                el.text = val
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
    except Exception as e:
        raise SerializationError(str(e))

def load_inventory_xml(filepath: str) -> Inventory:
    """Загружает Inventory из XML файл."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        raise SerializationError(str(e))
    data = {"products": []}
    for prod_el in root.findall("./products/product"):
        pid = prod_el.get("id")
        name = prod_el.findtext("name") or ""
        description = prod_el.findtext("description") or ""
        price = float(prod_el.findtext("price") or 0.0)
        stock = int(prod_el.findtext("stock") or 0)
        category = prod_el.findtext("category") or None
        data["products"].append({
            "id": pid,
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "category": category
        })
    inv = Inventory()
    inv.from_dict(data)
    return inv
