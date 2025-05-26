"""
Common test fixtures and utilities for all tests.
This file is automatically discovered by pytest and makes fixtures available across all test files.
"""
import pytest
import uuid
import os
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.data.database import get_db, Base
from src.data.tables import *  # Import all models
from src.main import app


@pytest.fixture(scope="function")
def test_db():
    """Create fresh database for each test"""
    # Create unique database file for each test
    db_filename = f"test_db_{uuid.uuid4().hex}.sqlite"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///./{db_filename}"
    test_engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Ensure all models are imported before creating tables
    from src.data.tables.customer import Customer
    from src.data.tables.location import Location
    from src.data.tables.product import Product
    from src.data.tables.purchase_rollup import PurchaseRollup
    from src.data.tables.purchase_product import PurchaseProduct
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal
    
    # Clean up
    Base.metadata.drop_all(bind=test_engine)
    if get_db in app.dependency_overrides:
        del app.dependency_overrides[get_db]
    
    # Remove test database file
    if os.path.exists(db_filename):
        os.remove(db_filename)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client"""
    return TestClient(app)


# Common test data creation utilities
class TestDataFactory:
    """Factory class for creating common test data"""
    
    @staticmethod
    def create_billing_location(db, **kwargs):
        """Create a billing location with optional overrides"""
        from src.data.tables.location import Location, LocationType
        
        defaults = {
            "location_type": LocationType.BILLING,
            "address_line_1": "123 Main St",
            "address_line_2": "Apt 1",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345"
        }
        defaults.update(kwargs)
        
        location = Location(**defaults)
        db.add(location)
        db.flush()
        return location
    
    @staticmethod
    def create_shipping_location(db, **kwargs):
        """Create a shipping location with optional overrides"""
        from src.data.tables.location import Location, LocationType
        
        defaults = {
            "location_type": LocationType.SHIPPING,
            "address_line_1": "456 Oak Ave",
            "address_line_2": "",
            "city": "Other City",
            "state": "NY",
            "zip_code": "54321"
        }
        defaults.update(kwargs)
        
        location = Location(**defaults)
        db.add(location)
        db.flush()
        return location
    
    @staticmethod
    def create_store_location(db, **kwargs):
        """Create a store location with optional overrides"""
        from src.data.tables.location import Location, LocationType
        
        defaults = {
            "location_type": LocationType.STORE,
            "address_line_1": "555 Store Ave",
            "address_line_2": "",
            "city": "Store City",
            "state": "CA",
            "zip_code": "55555"
        }
        defaults.update(kwargs)
        
        location = Location(**defaults)
        db.add(location)
        db.flush()
        return location
    
    @staticmethod
    def create_customer(db, billing_location_id, **kwargs):
        """Create a customer with optional overrides"""
        from src.data.tables.customer import Customer
        
        defaults = {
            "email": "test@example.com",
            "phone_number": "1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "billing_location_id": billing_location_id
        }
        defaults.update(kwargs)
        
        customer = Customer(**defaults)
        db.add(customer)
        db.flush()
        return customer
    
    @staticmethod
    def create_product(db, **kwargs):
        """Create a product with optional overrides"""
        from src.data.tables.product import Product
        
        defaults = {
            "name": "Widget A",
            "description": "A useful widget",
            "price": 1000
        }
        defaults.update(kwargs)
        
        product = Product(**defaults)
        db.add(product)
        db.flush()
        return product
    
    @staticmethod
    def create_purchase_rollup(db, customer_id, **kwargs):
        """Create a purchase rollup with optional overrides"""
        from src.data.tables.purchase_rollup import PurchaseRollup
        
        defaults = {
            "customer_id": customer_id,
            "total_cost": 1000
        }
        defaults.update(kwargs)
        
        purchase = PurchaseRollup(**defaults)
        db.add(purchase)
        db.flush()
        return purchase
    
    @staticmethod
    def create_purchase_product(db, product_id, shipping_location_id, purchase_rollup_id, **kwargs):
        """Create a purchase product with optional overrides"""
        from src.data.tables.purchase_product import PurchaseProduct
        
        defaults = {
            "product_id": product_id,
            "shipping_location_id": shipping_location_id,
            "purchase_rollup_id": purchase_rollup_id
        }
        defaults.update(kwargs)
        
        purchase_product = PurchaseProduct(**defaults)
        db.add(purchase_product)
        db.flush()
        return purchase_product


@pytest.fixture(scope="function")
def basic_sample_data(test_db):
    """Create basic sample data (customer with billing/shipping locations, products)"""
    db = test_db()
    factory = TestDataFactory()
    
    # Create locations
    billing_location = factory.create_billing_location(db)
    shipping_location = factory.create_shipping_location(db)
    
    # Create customer
    customer = factory.create_customer(db, billing_location.id)
    
    # Create products
    product1 = factory.create_product(db)
    product2 = factory.create_product(db, name="Widget B", description="Another widget", price=2000)
    
    db.commit()
    
    data = {
        "customer_id": customer.id,
        "billing_location_id": billing_location.id,
        "shipping_location_id": shipping_location.id,
        "product1_id": product1.id,
        "product2_id": product2.id
    }
    
    db.close()
    return data


@pytest.fixture(scope="function")
def analytics_sample_data(test_db):
    """Create comprehensive sample data for analytics testing"""
    db = test_db()
    factory = TestDataFactory()
    
    # Create billing locations in different zip codes
    billing_location_1 = factory.create_billing_location(db, zip_code="12345")
    billing_location_2 = factory.create_billing_location(
        db, 
        address_line_1="456 Oak Ave",
        city="Other City",
        state="NY",
        zip_code="54321"
    )
    
    # Create shipping locations in different zip codes
    shipping_location_1 = factory.create_shipping_location(
        db,
        address_line_1="789 Pine St",
        city="Ship City",
        state="TX", 
        zip_code="78901"
    )
    shipping_location_2 = factory.create_shipping_location(
        db,
        address_line_1="321 Elm St",
        city="Another City",
        state="FL",
        zip_code="32109"
    )
    
    # Create store locations
    store_location_1 = factory.create_store_location(db)
    store_location_2 = factory.create_store_location(
        db,
        address_line_1="777 Mall Blvd",
        city="Mall City",
        state="NY",
        zip_code="77777"
    )
    
    # Create customers
    customer_1 = factory.create_customer(db, billing_location_1.id, email="customer1@example.com", phone_number="1111111111")
    customer_2 = factory.create_customer(db, billing_location_2.id, email="customer2@example.com", phone_number="2222222222", first_name="Jane", last_name="Smith")
    customer_3 = factory.create_customer(db, billing_location_1.id, email="customer3@example.com", phone_number="3333333333", first_name="Bob", last_name="Johnson")
    
    # Create products
    product_1 = factory.create_product(db)
    product_2 = factory.create_product(db, name="Widget B", description="Another widget", price=2000)
    
    # Create purchase rollups - multiple orders for different customers
    purchase_1 = factory.create_purchase_rollup(db, customer_1.id, total_cost=1000)
    purchase_2 = factory.create_purchase_rollup(db, customer_1.id, total_cost=3000)
    purchase_3 = factory.create_purchase_rollup(db, customer_2.id, total_cost=2000)
    purchase_4 = factory.create_purchase_rollup(db, customer_3.id, total_cost=1000)
    purchase_5 = factory.create_purchase_rollup(db, customer_1.id, total_cost=2000)  # Customer 1 has most orders
    
    # Create purchase products with various shipping locations and times
    factory.create_purchase_product(
        db, product_1.id, shipping_location_1.id, purchase_1.id,
        created_at=datetime(2024, 1, 1, 9, 0, 0)  # 9 AM
    )
    factory.create_purchase_product(
        db, product_2.id, shipping_location_2.id, purchase_2.id,
        created_at=datetime(2024, 1, 1, 14, 0, 0)  # 2 PM
    )
    factory.create_purchase_product(
        db, product_1.id, shipping_location_1.id, purchase_3.id,
        created_at=datetime(2024, 1, 1, 10, 0, 0)  # 10 AM
    )
    
    # Store pickup purchases
    factory.create_purchase_product(
        db, product_2.id, store_location_1.id, purchase_4.id,
        created_at=datetime(2024, 1, 1, 11, 0, 0)  # 11 AM
    )
    factory.create_purchase_product(
        db, product_1.id, store_location_1.id, purchase_5.id,
        created_at=datetime(2024, 1, 1, 11, 30, 0)  # 11:30 AM (same hour as previous)
    )
    factory.create_purchase_product(
        db, product_2.id, store_location_2.id, purchase_2.id,
        created_at=datetime(2024, 1, 1, 15, 0, 0)  # 3 PM
    )
    
    db.commit()
    
    data = {
        "customer_1_id": customer_1.id,
        "customer_2_id": customer_2.id,
        "customer_3_id": customer_3.id,
        "billing_zip_12345": billing_location_1.zip_code,
        "billing_zip_54321": billing_location_2.zip_code,
        "shipping_zip_78901": shipping_location_1.zip_code,
        "shipping_zip_32109": shipping_location_2.zip_code,
        "store_zip_55555": store_location_1.zip_code,
        "store_zip_77777": store_location_2.zip_code
    }
    
    db.close()
    return data