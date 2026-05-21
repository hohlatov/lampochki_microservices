from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
import models, schemas, service
from database import engine, get_db
from auth import get_current_admin
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Сервис заказов — Лампочки")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Публичные эндпоинты (оформление заказа клиентом)
# ---------------------------------------------------------------------------

@app.post("/orders/", response_model=schemas.OrderCreatedResponse, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Создать заказ.
    Клиент передаёт product_id и quantity — цена берётся из products_service.
    """
    created = service.place_order(db, order)
    return schemas.OrderCreatedResponse(
        order_id=created.id,
        status=created.status,
        total_amount=created.total_amount,
        message=f"Заказ оформлен. Номер заказа: {created.id[:8]}...",
    )


# ---------------------------------------------------------------------------
# Админские эндпоинты (требуют JWT)
# ---------------------------------------------------------------------------

@app.get("/admin/orders/", response_model=List[schemas.OrderOut])
def admin_get_all_orders(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return service.list_orders(db)


@app.get("/admin/orders/{order_id}", response_model=schemas.OrderOut)
def admin_get_order(
    order_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return service.get_order_or_404(db, order_id)


@app.put("/admin/orders/{order_id}/status", response_model=schemas.OrderOut)
def admin_update_order_status(
    order_id: str,
    body: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return service.change_status(db, order_id, body.status)
