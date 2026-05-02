"""
HTTP-клиент для взаимодействия с products_service.
Все запросы к соседнему микросервису идут через этот модуль.
"""
import urllib.request
import urllib.error
import json
from fastapi import HTTPException

PRODUCTS_SERVICE_URL = "http://localhost:8000"


def _get(path: str) -> dict:
    url = f"{PRODUCTS_SERVICE_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        raise HTTPException(status_code=e.code, detail=body.get("detail", str(e)))
    except urllib.error.URLError:
        raise HTTPException(status_code=503, detail="products_service недоступен")


def _patch(path: str, payload: dict) -> dict:
    url = f"{PRODUCTS_SERVICE_URL}{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="PATCH",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        raise HTTPException(status_code=e.code, detail=body.get("detail", str(e)))
    except urllib.error.URLError:
        raise HTTPException(status_code=503, detail="products_service недоступен")


def get_product(product_id: str) -> dict:
    """Получить данные о товаре (цена, название, остаток)."""
    return _get(f"/products/{product_id}")


def decrease_stock(product_id: str, quantity: int) -> dict:
    """Уменьшить остаток товара на quantity единиц."""
    return _patch(f"/internal/products/{product_id}/stock", {"quantity": -quantity})


def increase_stock(product_id: str, quantity: int) -> dict:
    """Увеличить остаток товара (например, при отмене заказа)."""
    return _patch(f"/internal/products/{product_id}/stock", {"quantity": quantity})
