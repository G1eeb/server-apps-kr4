from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Product

router = APIRouter(prefix="/products", tags=["products"])

# Pydantic схемы
class ProductCreate(BaseModel):
    title: str
    price: float
    count: int

class ProductResponse(ProductCreate):
    id: int
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    description: str

# Добавление записи в таблицу Product (Задание 9.1)
@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.patch("/{product_id}/description")
def update_description(product_id: int, update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.description = update.description
    db.commit()
    db.refresh(product)
    return product