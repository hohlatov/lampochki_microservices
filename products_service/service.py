"""
Сервисный слой products_service.
Содержит бизнес-логику, отделённую от слоя HTTP (main.py) и слоя БД (crud.py).
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
import crud, schemas


def fetch_all_products(db: Session):
    return crud.get_all_products(db)


def fetch_product_or_404(db: Session, product_id: str):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


def add_product(db: Session, data: schemas.ProductCreate):
    return crud.create_product(db, data)


def edit_product(db: Session, product_id: str, data: schemas.ProductCreate):
    product = crud.update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


def remove_product(db: Session, product_id: str):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Товар не найден")


def update_stock(db: Session, product_id: str, quantity: int):
    """
    Изменяет остаток товара.
    Вызывается orders_service через внутренний эндпоинт при оформлении заказа.
    """
    result = crud.change_stock(db, product_id, quantity)
    if result is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if result is False:
        raise HTTPException(
            status_code=409,
            detail="Недостаточно товара на складе"
        )
    return result
