def _normalize_inventory_entry(entry):
    if isinstance(entry, dict):
        return {
            "qty": entry.get("qty", 0),
            "unit": (entry.get("unit") or "pcs").lower(),
            "type": (entry.get("type") or "count").lower(),
        }
    return {"qty": entry, "unit": "pcs", "type": "count"}


def _threshold(item_type, unit):
    if item_type == "liquid" or unit in ("ml", "l"):
        return 150
    return 6


def check_alerts(temp, inventory):
    alerts = []

    if temp is None:
        alerts.append("⚠️ Temperature sensor unavailable.")
    else:
        if temp > 10:
            alerts.append("🔴 Temperature is dangerous! Immediate action required.")
        elif temp > 8:
            alerts.append("⚠️ Temperature too high!")
        elif temp < 1:
            alerts.append("❄️ Temperature too low!")

    for item_name, entry in (inventory or {}).items():
        normalized = _normalize_inventory_entry(entry)
        qty = normalized["qty"]
        unit = normalized["unit"]
        item_type = normalized["type"]
        threshold = _threshold(item_type, unit)

        if qty <= 0:
            alerts.append(f"⚠️ {item_name} is out of stock.")
        elif qty < threshold:
            alerts.append(f"⚠️ {item_name} is running low: {qty} {unit} left.")

    return alerts