inventory = {}

def _normalize_inventory():
    for key, value in list(inventory.items()):
        if isinstance(value, dict):
            inventory[key] = {
                "qty": value.get("qty", 0),
                "unit": value.get("unit", "pcs"),
                "type": value.get("type", "count"),
            }
        else:
            inventory[key] = {"qty": value, "unit": "pcs", "type": "count"}
    return inventory


def add_inventory(item, qty, unit="pcs", type="count"):
    item_key = item.strip().lower()
    if not item_key or qty <= 0:
        return
    _normalize_inventory()
    existing = inventory.get(item_key)
    if existing:
        existing["qty"] += qty
        existing["unit"] = unit or existing["unit"]
        existing["type"] = type or existing["type"]
    else:
        inventory[item_key] = {
            "qty": qty,
            "unit": unit or "pcs",
            "type": type or "count",
        }

def remove_inventory(item, qty=None):
    item_key = item.strip().lower()
    existing = inventory.get(item_key)
    if not existing:
        return
    if qty is None or qty <= 0 or qty >= existing["qty"]:
        inventory.pop(item_key, None)
    else:
        existing["qty"] -= qty

def remove_inventory_items(items):
    for item in items:
        remove_inventory(item)

def get_inventory():
    return _normalize_inventory()

def get_low_items():
    low_items = {}
    for key, item in _normalize_inventory().items():
        if item["type"] == "liquid" and item["qty"] < 150:
            low_items[key] = item
        elif item["type"] == "count" and item["qty"] < 6:
            low_items[key] = item
    return low_items