from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.data.database import Base


class PurchaseRollup(Base):
    __tablename__ = "purchase_rollup"

    id = Column(Integer, primary_key=True, index=True)

    # what customer bought this?
    customer_id = Column(Integer, ForeignKey('customer.id'))

    # Total price customer paid for this order. Probably just sum of all
    # product costs but could also include a bulk discount or something
    total_cost = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
