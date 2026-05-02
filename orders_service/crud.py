from sqlalchemy.orm import Session
import models
import uuid


def get_all_orders(db: Session):
    return db.query(models.Order).all()


def get_order(db: Session, order_id: str):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, customer_name: str, customer_phone: str,
                 delivery_address: str, payment_method: str,
                 items_data: list, total_amount: float):
    """
    Сохраняет заказ в БД. items_data — список словарей с уже проверенными
    и обогащёнными данными (product_id, product_name, quantity, price_at_time).
    """
    order = models.Order(
        id=str(uuid.uuid4()),
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        payment_method=payment_method,
        total_amount=total_amount,
        status="new"
    )
    db.add(order)
    db.flush()

    for item in items_data:
        order_item = models.OrderItem(
            id=str(uuid.uuid4()),
            order_id=order.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            quantity=item["quantity"],
            price_at_time=item["price_at_time"]
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order_id: str, status: str):
    order = get_order(db, order_id)
    if not order:
        return None
    order.status = status
    db.commit()
    db.refresh(order)
    return order
