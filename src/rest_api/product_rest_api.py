from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.data.database import get_db
from src.services.product_service import ProductService
from src.rest_api.schemas import ProductCreate, ProductResponse

product_router = APIRouter(
    prefix="/product",
    tags=["customer"]
)


@product_router.post("/products/", response_model=ProductResponse)
def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.create_product(request)


@product_router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@product_router.get("/products/by-name/{name}", response_model=ProductResponse)
def get_product_by_name(name: str, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    product = product_service.get_product_by_name(name)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
