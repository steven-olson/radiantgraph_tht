from sqlalchemy.orm import Session
from src.data.tables.purchase_rollup import PurchaseRollup
from src.data.tables.purchase_product import PurchaseProduct
from src.data.tables.location import Location, LocationType
from src.data.tables.product import Product
from src.data.tables.customer import Customer
from src.rest_api.schemas import PurchaseCreate
from typing import Optional


class PurchaseService:

    def __init__(self, db: Session):
        self.db = db

    def _validate_customer(self, customer_id: int) -> Customer:
        """Validate that customer exists and return customer object."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with id {customer_id} not found")
        return customer

    def _validate_product(self, product_id: int) -> Product:
        """Validate that product exists and return product object."""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with id {product_id} not found")
        return product

    def _resolve_shipping_location(self, item, customer: Customer) -> int:
        """Resolve shipping location and return location ID."""
        if item.ship_to_billing_address:
            # Use customer's billing address
            return customer.billing_location_id
        elif item.shipping_location_id:
            # Use existing location by ID
            existing_location = self.db.query(Location).filter(Location.id == item.shipping_location_id).first()
            if not existing_location:
                raise ValueError(f"Location with id {item.shipping_location_id} not found")
            return item.shipping_location_id
        elif item.shipping_location:
            # Create new shipping location
            shipping_location = Location(
                location_type=LocationType.SHIPPING,
                address_line_1=item.shipping_location.address_line_1,
                address_line_2=item.shipping_location.address_line_2 or "",
                city=item.shipping_location.city,
                state=item.shipping_location.state,
                zip_code=item.shipping_location.zip_code
            )
            self.db.add(shipping_location)
            self.db.flush()
            return shipping_location.id
        else:
            raise ValueError("No shipping location specified")

    def _process_purchase_items(self, items, customer: Customer) -> tuple[int, list[tuple[int, int]]]:
        """Process all purchase items and return total cost and product data."""
        total_cost = 0
        product_data = []
        
        for item in items:
            # Validate product exists
            product = self._validate_product(item.product_id)
            
            # Resolve shipping location
            shipping_location_id = self._resolve_shipping_location(item, customer)
            
            total_cost += product.price
            product_data.append((item.product_id, shipping_location_id))
        
        return total_cost, product_data

    def _create_purchase_records(self, customer_id: int, total_cost: int, product_data: list[tuple[int, int]]) -> PurchaseRollup:
        """Create purchase rollup and purchase product records."""
        # Create purchase rollup
        purchase_rollup = PurchaseRollup(
            customer_id=customer_id,
            total_cost=total_cost
        )
        self.db.add(purchase_rollup)
        self.db.flush()
        
        # Create purchase products
        for product_id, shipping_location_id in product_data:
            purchase_product = PurchaseProduct(
                product_id=product_id,
                shipping_location_id=shipping_location_id,
                purchase_rollup_id=purchase_rollup.id
            )
            self.db.add(purchase_product)
        
        self.db.commit()
        self.db.refresh(purchase_rollup)
        return purchase_rollup

    def create_purchase(self, request: PurchaseCreate) -> PurchaseRollup:
        """Create a new purchase with products and shipping locations."""
        # Validate customer exists
        customer = self._validate_customer(request.customer_id)
        
        # Process all purchase items
        total_cost, product_data = self._process_purchase_items(request.products, customer)
        
        # Create purchase records
        return self._create_purchase_records(request.customer_id, total_cost, product_data)

    def get_purchase_by_id(self, purchase_id: int) -> Optional[PurchaseRollup]:
        return self.db.query(PurchaseRollup).filter(PurchaseRollup.id == purchase_id).first()
