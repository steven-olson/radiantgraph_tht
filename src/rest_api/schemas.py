from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from enum import Enum


class LocationTypeEnum(str, Enum):
    BILLING = "billing"
    SHIPPING = "shipping"
    STORE = "store"


class LocationCreate(BaseModel):
    location_type: LocationTypeEnum
    address_line_1: str
    address_line_2: Optional[str] = ""
    city: str
    state: str
    zip_code: str


class LocationResponse(LocationCreate):
    id: int
    
    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    billing_address: LocationCreate


class CustomerResponse(BaseModel):
    id: int
    email: str
    phone_number: str
    first_name: str
    last_name: str
    billing_location_id: int
    
    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: str
    price: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    
    class Config:
        from_attributes = True


class PurchaseProductItem(BaseModel):
    product_id: int
    shipping_location: Optional[LocationCreate] = None
    shipping_location_id: Optional[int] = None
    ship_to_billing_address: bool = False
    
    @validator('ship_to_billing_address', always=True)
    def validate_shipping_options(cls, v, values):
        shipping_location = values.get('shipping_location')
        shipping_location_id = values.get('shipping_location_id')
        
        # Count how many shipping options are provided
        options_provided = sum([
            v,  # ship_to_billing_address
            shipping_location is not None,
            shipping_location_id is not None
        ])
        
        if options_provided == 0:
            raise ValueError('At least one shipping option must be specified: ship_to_billing_address, shipping_location, or shipping_location_id')
        elif options_provided > 1:
            raise ValueError('Only one shipping option can be specified: ship_to_billing_address, shipping_location, or shipping_location_id')
        
        return v


class PurchaseCreate(BaseModel):
    customer_id: int
    products: list[PurchaseProductItem]


class PurchaseProductResponse(BaseModel):
    id: int
    purchase_rollup_id: int
    product_id: int
    shipping_location_id: int
    
    class Config:
        from_attributes = True


class PurchaseRollupResponse(BaseModel):
    id: int
    customer_id: int
    total_cost: int
    
    class Config:
        from_attributes = True
