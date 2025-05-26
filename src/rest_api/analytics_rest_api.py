from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.data.database import get_db
from src.services.analytics_service import AnalyticsService
from typing import List, Dict, Any

analytics_router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)


@analytics_router.get("/orders-by-billing-zip", response_model=List[Dict[str, Any]])
def get_orders_by_billing_zip(
    ascending: bool = Query(False, description="Sort in ascending order if True, descending if False"),
    db: Session = Depends(get_db)
):
    analytics_service = AnalyticsService(db)
    results = analytics_service.get_order_count_by_billing_zip_code(ascending=ascending)
    return [{"zip_code": result.zip_code, "order_count": result.order_count} for result in results]


@analytics_router.get("/orders-by-shipping-zip", response_model=List[Dict[str, Any]])
def get_orders_by_shipping_zip(
    ascending: bool = Query(False, description="Sort in ascending order if True, descending if False"),
    db: Session = Depends(get_db)
):
    analytics_service = AnalyticsService(db)
    results = analytics_service.get_order_count_by_shipping_zip_code(ascending=ascending)
    return [{"zip_code": result.zip_code, "order_count": result.order_count} for result in results]


@analytics_router.get("/store-purchase-times", response_model=List[Dict[str, Any]])
def get_store_purchase_times(db: Session = Depends(get_db)):
    analytics_service = AnalyticsService(db)
    results = analytics_service.get_most_purchase_time_of_day()
    return [{"hour": int(result.hour), "purchase_count": result.purchase_count} for result in results]


@analytics_router.get("/top-store-pickup-users", response_model=List[Dict[str, Any]])
def get_top_store_pickup_users(db: Session = Depends(get_db)):
    analytics_service = AnalyticsService(db)
    results = analytics_service.get_users_with_most_store_pickups()
    return [
        {
            "customer_id": result.id,
            "first_name": result.first_name,
            "last_name": result.last_name,
            "email": result.email,
            "store_order_count": result.store_order_count
        }
        for result in results
    ]