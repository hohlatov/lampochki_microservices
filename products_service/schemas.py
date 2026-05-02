from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    name:        str
    description: Optional[str] = None
    price:       float = Field(..., gt=0)
    stock:       int   = Field(..., ge=0)
    wattage:     Optional[int] = None
    base_type:   Optional[str] = None
    image_url:   Optional[str] = None


class ProductOut(ProductCreate):
    id: str

    class Config:
        from_attributes = True


class StockUpdate(BaseModel):
    quantity: int = Field(..., description="На сколько изменить остаток (отрицательное — уменьшить)")
