from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path
from sensors import get_temperature
from inventory import (
    get_inventory,
    add_inventory,
    remove_inventory,
    remove_inventory_items,
)
from alerts import check_alerts
from ai import generate_recipe
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manual temperature override (used until a real sensor is connected).
# When sensors.py returns a real value, that takes priority.
_manual_temperature: Optional[float] = None


def _get_temp():
    """Return sensor temperature if available, otherwise the manual override."""
    sensor = get_temperature()
    if sensor is not None:
        return sensor
    return _manual_temperature


# ── Serve the frontend ────────────────────────────────────────────────────────
@app.get("/")
def home():
    html_path = Path(__file__).resolve().parent / "index.html"
    return FileResponse(str(html_path))


# ── Status ────────────────────────────────────────────────────────────────────
@app.get("/status")
def status():
    temp = _get_temp()
    inv = get_inventory()
    return {"temperature": temp, "inventory": inv}


# ── Temperature ───────────────────────────────────────────────────────────────
class TemperaturePayload(BaseModel):
    temperature: float


@app.post("/temperature/set")
def set_temperature(payload: TemperaturePayload):
    """
    Manually override the fridge temperature.
    Useful for testing before a real sensor is connected.
    Once sensors.py returns a real value, this override is ignored.
    """
    global _manual_temperature
    _manual_temperature = payload.temperature
    return {"temperature": _manual_temperature}


# ── Alerts ────────────────────────────────────────────────────────────────────
@app.get("/alerts")
def alerts():
    temp = _get_temp()
    inv = get_inventory()
    return {"alerts": check_alerts(temp, inv)}


# ── Recipe ────────────────────────────────────────────────────────────────────
@app.get("/recipe")
def recipe(meal: str):
    items = get_inventory()
    result = generate_recipe(items, meal)
    return {"recipe": result}


# ── Inventory ─────────────────────────────────────────────────────────────────
@app.get("/inventory")
def inventory_route():
    return {"inventory": get_inventory()}


class InventoryItem(BaseModel):
    item: str
    qty: int
    unit: str = "pcs"
    type: str = "count"


class InventoryRemoveItem(BaseModel):
    item: str
    qty: Optional[int] = None


class InventoryRemoveItems(BaseModel):
    items: List[str]


@app.post("/inventory/add")
def inventory_add(payload: InventoryItem):
    if not payload.item or payload.qty <= 0:
        raise HTTPException(status_code=400, detail="Invalid inventory item or quantity")
    add_inventory(payload.item, payload.qty, payload.unit, payload.type)
    return {"inventory": get_inventory()}


@app.post("/inventory/remove")
def inventory_remove(payload: InventoryRemoveItem):
    if not payload.item.strip():
        raise HTTPException(status_code=400, detail="Invalid inventory item")
    remove_inventory(payload.item, payload.qty)
    return {"inventory": get_inventory()}


@app.post("/inventory/remove-used")
def inventory_remove_used(payload: InventoryRemoveItems):
    if not payload.items:
        raise HTTPException(status_code=400, detail="No inventory items specified")
    remove_inventory_items(payload.items)
    return {"inventory": get_inventory()}


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
