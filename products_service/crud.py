from sqlalchemy.orm import Session
import models, schemas
import uuid


def get_all_products(db: Session):
    return db.query(models.Product).all()


def get_product(db: Session, product_id: str):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def create_product(db: Session, data: schemas.ProductCreate):
    product = models.Product(id=str(uuid.uuid4()), **data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: str, data: schemas.ProductCreate):
    product = get_product(db, product_id)
    if not product:
        return None
    for key, value in data.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: str):
    product = get_product(db, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


def change_stock(db: Session, product_id: str, quantity: int):
    """
    Изменяет остаток товара на указанное количество.
    quantity > 0 — увеличить, quantity < 0 — уменьшить.
    Возвращает None если товар не найден, False если недостаточно остатка.
    """
    product = get_product(db, product_id)
    if not product:
        return None
    new_stock = product.stock + quantity
    if new_stock < 0:
        return False
    product.stock = new_stock
    db.commit()
    db.refresh(product)
    return product
