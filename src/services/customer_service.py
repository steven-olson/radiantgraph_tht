from sqlalchemy.orm import Session
from src.data.tables.customer import Customer
from src.data.tables.location import Location, LocationType
from src.rest_api.schemas import CustomerCreate
from typing import Optional


class CustomerService:

    def __init__(self, db: Session):
        self.db = db

    def new_customer(self, request: CustomerCreate) -> Customer:
        # Create billing address first
        billing_location = Location(
            location_type=LocationType.BILLING,
            address_line_1=request.billing_address.address_line_1,
            address_line_2=request.billing_address.address_line_2 or "",
            city=request.billing_address.city,
            state=request.billing_address.state,
            zip_code=request.billing_address.zip_code
        )
        self.db.add(billing_location)
        self.db.flush()
        
        # Create customer with billing location ID
        customer = Customer(
            email=request.email,
            phone_number=request.phone_number,
            first_name=request.first_name,
            last_name=request.last_name,
            billing_location_id=billing_location.id
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        
        return customer

    def query_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.phone_number == phone_number).first()
    
    def query_customer_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email).first()
