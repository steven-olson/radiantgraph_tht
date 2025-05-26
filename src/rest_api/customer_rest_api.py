from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.data.database import get_db
from src.services.customer_service import CustomerService
from src.rest_api.schemas import CustomerCreate, CustomerResponse

customer_router = APIRouter(
    prefix="/customer",
    tags=["customer"]
)


@customer_router.post("/", response_model=CustomerResponse)
def new_customer(request: CustomerCreate, db: Session = Depends(get_db)):
    customer_service = CustomerService(db)
    return customer_service.new_customer(request)


@customer_router.get("/by-phone/{phone_number}", response_model=CustomerResponse)
def get_customer_by_phone(phone_number: str, db: Session = Depends(get_db)):
    customer_service = CustomerService(db)
    customer = customer_service.query_customer_by_phone(phone_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@customer_router.get("/by-email/{email}", response_model=CustomerResponse)
def get_customer_by_email(email: str, db: Session = Depends(get_db)):
    customer_service = CustomerService(db)
    customer = customer_service.query_customer_by_email(email)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


