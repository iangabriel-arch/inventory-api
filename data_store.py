"""
data_store.py

Simulated in-memory database for the inventory system.
"""

inventory = []
_next_id = 1


def get_all_items():
    return inventory


def get_item_by_id(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def add_item(data):
    global _next_id
    new_item = {
        "id": _next_id,
        "name": data.get("name"),
        "brand": data.get("brand"),
        "price": data.get("price"),
        "stock": data.get("stock", 0),
        "ingredients": data.get("ingredients"),
        "barcode": data.get("barcode"),
    }
    inventory.append(new_item)
    _next_id += 1
    return new_item


def update_item(item_id, data):
    item = get_item_by_id(item_id)
    if item is None:
        return None
    for key in ["name", "brand", "price", "stock", "ingredients", "barcode"]:
        if key in data:
            item[key] = data[key]
    return item


def delete_item(item_id):
    item = get_item_by_id(item_id)
    if item is None:
        return False
    inventory.remove(item)
    return True


def reset():
    """Helper used by tests to clear state between test cases."""
    global inventory, _next_id
    inventory = []
    _next_id = 1
