from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ---------- Входящие данные от клиента ----------

class OrderItemCreate(BaseModel):
    """
    Клиент передаёт только product_id и quantity.
    Цену и название сервис получает сам из products_service.
    """
    product_id: str
    quantity:   int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name:    str
    customer_phone:   str
    delivery_address: str
    payment_method:   str
    items:            List[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str


# ---------- Исходящие данные ----------

class OrderItemOut(BaseModel):
    id:            str
    product_id:    str
    product_name:  str
    quantity:      int
    price_at_time: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id:               str
    customer_name:    str
    customer_phone:   str
    delivery_address: str
    payment_method:   str
    status:           str
    total_amount:     float
    created_at:       datetime
    items:            List[OrderItemOut]

    class Config:
        from_attributes = True


class OrderCreatedResponse(BaseModel):
    order_id:     str
    status:       str
    total_amount: float
    message:      str
