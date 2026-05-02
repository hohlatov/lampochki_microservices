from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name    = Column(String(255), nullable=False)
    customer_phone   = Column(String(20),  nullable=False)
    delivery_address = Column(String,      nullable=False)
    payment_method   = Column(String(50),  nullable=False)
    status           = Column(String(50),  nullable=False, default="new")
    total_amount     = Column(Float,       nullable=False, default=0.0)
    created_at       = Column(DateTime,    default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id      = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id    = Column(String, nullable=False)
    product_name  = Column(String(255), nullable=False)
    quantity      = Column(Integer, nullable=False)
    price_at_time = Column(Float, nullable=False)  # цена получена из products_service

    order = relationship("Order", back_populates="items")
