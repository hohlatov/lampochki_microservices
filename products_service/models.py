from sqlalchemy import Column, String, Float, Integer
from database import Base
import uuid


class Product(Base):
    __tablename__ = "products"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name        = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    price       = Column(Float, nullable=False)
    stock       = Column(Integer, nullable=False, default=0)
    wattage     = Column(Integer, nullable=True)
    base_type   = Column(String(50), nullable=True)
    image_url   = Column(String, nullable=True)
