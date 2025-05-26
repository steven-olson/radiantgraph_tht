from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.data.database import Base


class PurchaseProduct(Base):
    __tablename__ = "purchase_product"

    id = Column(Integer, primary_key=True, index=True)

    # fk to the product bought
    product_id = Column(Integer, ForeignKey('product.id'))

    # fk to the location this should be shipped to
    shipping_location_id = Column(Integer, ForeignKey('location.id'))

    # fk to purchase rollup, ie as part of what "order" did a customer
    # buy this product
    purchase_rollup_id = Column(Integer, ForeignKey('purchase_rollup.id'))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
