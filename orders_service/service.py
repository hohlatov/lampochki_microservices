"""
Сервисный слой orders_service.
Здесь сосредоточена вся бизнес-логика:
  - проверка товаров через products_service
  - проверка наличия (stock)
  - расчёт суммы по реальным ценам
  - резервирование остатков
  - сохранение заказа через crud
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
import crud, schemas, products_client


ALLOWED_STATUSES = {"new", "processing", "shipped", "delivered", "cancelled"}


def place_order(db: Session, data: schemas.OrderCreate):
    """
    Оформляет заказ:
    1. Для каждой позиции запрашивает products_service → получает цену и название
    2. Проверяет, что stock >= quantity
    3. Рассчитывает итоговую сумму
    4. Уменьшает stock в products_service
    5. Сохраняет заказ в БД
    """
    enriched_items = []
    total = 0.0

    # Шаг 1-2: проверяем каждый товар в products_service
    for order_item in data.items:
        product = products_client.get_product(order_item.product_id)
        # get_product бросит HTTPException 404 если товар не найден

        if product["stock"] < order_item.quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Недостаточно товара «{product['name']}» на складе "
                       f"(доступно: {product['stock']}, запрошено: {order_item.quantity})"
            )

        enriched_items.append({
            "product_id":    order_item.product_id,
            "product_name":  product["name"],
            "quantity":      order_item.quantity,
            "price_at_time": product["price"],
        })
        total += product["price"] * order_item.quantity

    # Шаг 3: резервируем остатки (уменьшаем stock)
    reserved = []
    try:
        for item in enriched_items:
            products_client.decrease_stock(item["product_id"], item["quantity"])
            reserved.append(item)
    except HTTPException:
        # Если не удалось зарезервировать — откатываем уже уменьшенные остатки
        for item in reserved:
            products_client.increase_stock(item["product_id"], item["quantity"])
        raise

    # Шаг 4: сохраняем заказ
    order = crud.create_order(
        db=db,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        payment_method=data.payment_method,
        items_data=enriched_items,
        total_amount=round(total, 2),
    )
    return order


def get_order_or_404(db: Session, order_id: str):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order


def change_status(db: Session, order_id: str, status: str):
    if status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Недопустимый статус. Допустимые значения: {', '.join(ALLOWED_STATUSES)}"
        )
    order = crud.update_order_status(db, order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order


def list_orders(db: Session):
    return crud.get_all_orders(db)
