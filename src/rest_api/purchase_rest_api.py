from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.data.database import get_db
from src.services.purchase_service import PurchaseService
from src.rest_api.schemas import PurchaseCreate, PurchaseRollupResponse


purchase_router = APIRouter(
    prefix="/purchase",
    tags=["purchase"]
)


@purchase_router.post("/", response_model=PurchaseRollupResponse)
def new_purchase(request: PurchaseCreate, db: Session = Depends(get_db)):
    purchase_service = PurchaseService(db)
    try:
        return purchase_service.create_purchase(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@purchase_router.get("/{purchase_id}", response_model=PurchaseRollupResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase_service = PurchaseService(db)
    purchase = purchase_service.get_purchase_by_id(purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase
