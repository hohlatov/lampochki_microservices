from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
import models, schemas, service
from database import engine, get_db
from auth import LoginRequest, Token, authenticate_user, create_access_token, get_current_admin, get_current_user
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Сервис товаров — Лампочки")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Публичные эндпоинты
# ---------------------------------------------------------------------------

@app.get("/products", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    return service.fetch_all_products(db)


@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    return service.fetch_product_or_404(db, product_id)


@app.post("/products/", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return service.add_product(db, product)


@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: str, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return service.edit_product(db, product_id, product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    service.remove_product(db, product_id)


# ---------------------------------------------------------------------------
# Внутренний эндпоинт — вызывается только из orders_service
# ---------------------------------------------------------------------------

@app.patch("/internal/products/{product_id}/stock", response_model=schemas.ProductOut)
def patch_stock(product_id: str, body: schemas.StockUpdate, db: Session = Depends(get_db)):
    """
    Изменяет остаток товара.
    body.quantity = -2  → уменьшить на 2 (резервирование при заказе)
    body.quantity = +2  → увеличить на 2 (отмена заказа)
    """
    return service.update_stock(db, product_id, body.quantity)


# ---------------------------------------------------------------------------
# Админские эндпоинты
# ---------------------------------------------------------------------------

@app.get("/admin/products", response_model=List[schemas.ProductOut])
def admin_get_products(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)  
):
    return service.fetch_all_products(db)

@app.post("/admin/products", response_model=schemas.ProductOut, status_code=201)
def admin_create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)  
):
    return service.add_product(db, product)

@app.put("/admin/products/{product_id}", response_model=schemas.ProductOut)
def admin_update_product(
    product_id: str,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)  
):
    return service.edit_product(db, product_id, product)

@app.delete("/admin/products/{product_id}", status_code=204)
def admin_delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)  
):
    service.remove_product(db, product_id)


# ---------- Аутентификация ----------
@app.post("/auth/login", response_model=Token)
def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

