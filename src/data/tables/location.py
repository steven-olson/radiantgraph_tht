from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from src.data.database import Base
from enum import Enum


class LocationType(Enum):
    BILLING = "billing"
    SHIPPING = "shipping"
    STORE = "store"


class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, index=True)
    location_type = Column(SQLEnum(LocationType))
    address_line_1 = Column(String, unique=False, nullable=False)
    address_line_2 = Column(String, unique=False, nullable=False)
    city = Column(String, unique=False, nullable=False)
    state = Column(String, unique=False, nullable=False)
    zip_code = Column(String, unique=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
