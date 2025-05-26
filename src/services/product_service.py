from sqlalchemy.orm import Session
from src.data.tables.product import Product
from src.rest_api.schemas import ProductCreate
from typing import Optional


class ProductService:

    def __init__(self, db: Session):
        self.db = db

    def create_product(self, request: ProductCreate) -> Product:
        product = Product(
            name=request.name,
            description=request.description,
            price=request.price
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_by_name(self, name: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.name == name).first()