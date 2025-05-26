from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from src.data.tables.customer import Customer
from src.data.tables.location import Location, LocationType
from src.data.tables.purchase_rollup import PurchaseRollup
from src.data.tables.purchase_product import PurchaseProduct


class AnalyticsService:

    def __init__(self, db: Session):
        self.db = db

    def get_order_count_by_billing_zip_code(self, ascending=False):
        """
        Show a total count of orders aggregated by billing zip code, descending or
        ascending.
        :param ascending:
        :return:
        """
        query = (
            self.db.query(
                Location.zip_code,
                func.count(PurchaseRollup.id).label('order_count')
            )
            .join(Customer, Customer.billing_location_id == Location.id)
            .join(PurchaseRollup, PurchaseRollup.customer_id == Customer.id)
            .group_by(Location.zip_code)
            .order_by(func.count(PurchaseRollup.id).asc() if ascending else func.count(PurchaseRollup.id).desc())
        )
        return query.all()

    def get_order_count_by_shipping_zip_code(self, ascending=False):
        """
        Show a total count of orders aggregated by shipping zip code, descending or
        ascending
        :param ascending:
        :return:
        """
        query = (
            self.db.query(
                Location.zip_code,
                func.count(func.distinct(PurchaseRollup.id)).label('order_count')
            )
            .join(PurchaseProduct, PurchaseProduct.shipping_location_id == Location.id)
            .join(PurchaseRollup, PurchaseRollup.id == PurchaseProduct.purchase_rollup_id)
            .group_by(Location.zip_code)
            .order_by(func.count(func.distinct(PurchaseRollup.id)).asc() if ascending else func.count(func.distinct(PurchaseRollup.id)).desc())
        )
        return query.all()

    def get_most_purchase_time_of_day(self):
        """
        Can you tell me what times of day most in-store purchases are made? An in store order is one
        where a roll-up order contained a product that was shipped to a location that has
        location_type equal to `STORE`. Use the `created_at` field of the `purchase_product`
        table rounded to the hour.
        :return:
        """
        query = (
            self.db.query(
                extract('hour', PurchaseProduct.created_at).label('hour'),
                func.count(PurchaseProduct.id).label('purchase_count')
            )
            .join(Location, Location.id == PurchaseProduct.shipping_location_id)
            .filter(Location.location_type == LocationType.STORE)
            .group_by(extract('hour', PurchaseProduct.created_at))
            .order_by(func.count(PurchaseProduct.id).desc())
        )
        return query.all()

    def get_users_with_most_store_pickups(self):
        """
        List top 5 users with the most number of in-store orders. An in store order is one
        where a roll-up order contained a product that was shipped to a location that has
        location_type equal to `STORE`.
        :return:
        """
        query = (
            self.db.query(
                Customer.id,
                Customer.first_name,
                Customer.last_name,
                Customer.email,
                func.count(func.distinct(PurchaseRollup.id)).label('store_order_count')
            )
            .join(PurchaseRollup, PurchaseRollup.customer_id == Customer.id)
            .join(PurchaseProduct, PurchaseProduct.purchase_rollup_id == PurchaseRollup.id)
            .join(Location, Location.id == PurchaseProduct.shipping_location_id)
            .filter(Location.location_type == LocationType.STORE)
            .group_by(Customer.id, Customer.first_name, Customer.last_name, Customer.email)
            .order_by(func.count(func.distinct(PurchaseRollup.id)).desc())
            .limit(5)
        )
        return query.all()
