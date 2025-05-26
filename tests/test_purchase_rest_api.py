import pytest
from fastapi.testclient import TestClient


class TestPurchaseEndpoints:
    
    def test_create_purchase_with_billing_address(self, client, basic_sample_data, test_db):
        """Test purchase creation using billing address"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "ship_to_billing_address": True
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == basic_sample_data["customer_id"]
        assert data["total_cost"] == 1000
        assert "id" in data
        
        # Verify data was persisted in database
        from src.data.tables.purchase_rollup import PurchaseRollup
        from src.data.tables.purchase_product import PurchaseProduct
        db = test_db()
        purchase = db.query(PurchaseRollup).filter(PurchaseRollup.id == data["id"]).first()
        assert purchase is not None
        assert purchase.total_cost == 1000
        
        # Verify purchase product was created
        purchase_product = db.query(PurchaseProduct).filter(
            PurchaseProduct.purchase_rollup_id == purchase.id
        ).first()
        assert purchase_product is not None
        assert purchase_product.product_id == basic_sample_data["product1_id"]
        assert purchase_product.shipping_location_id == basic_sample_data["billing_location_id"]
        db.close()
    
    def test_create_purchase_with_existing_location(self, client, basic_sample_data, test_db):
        """Test purchase creation using existing shipping location"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "shipping_location_id": basic_sample_data["shipping_location_id"],
                    "ship_to_billing_address": False
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == basic_sample_data["customer_id"]
        assert data["total_cost"] == 1000
        
        # Verify purchase product uses correct shipping location
        from src.data.tables.purchase_product import PurchaseProduct
        db = test_db()
        purchase_product = db.query(PurchaseProduct).filter(
            PurchaseProduct.purchase_rollup_id == data["id"]
        ).first()
        assert purchase_product.shipping_location_id == basic_sample_data["shipping_location_id"]
        db.close()
    
    def test_create_purchase_with_new_location(self, client, basic_sample_data, test_db):
        """Test purchase creation with new shipping location"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "ship_to_billing_address": False,
                    "shipping_location": {
                        "location_type": "shipping",
                        "address_line_1": "789 Pine St",
                        "address_line_2": "Suite 100",
                        "city": "New City",
                        "state": "TX",
                        "zip_code": "78901"
                    }
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == basic_sample_data["customer_id"]
        assert data["total_cost"] == 1000
        
        # Verify new location was created
        from src.data.tables.purchase_product import PurchaseProduct
        from src.data.tables.location import Location
        db = test_db()
        purchase_product = db.query(PurchaseProduct).filter(
            PurchaseProduct.purchase_rollup_id == data["id"]
        ).first()
        
        new_location = db.query(Location).filter(
            Location.id == purchase_product.shipping_location_id
        ).first()
        assert new_location.address_line_1 == "789 Pine St"
        assert new_location.city == "New City"
        db.close()
    
    def test_create_purchase_multiple_products(self, client, basic_sample_data, test_db):
        """Test purchase creation with multiple products and different shipping options"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "ship_to_billing_address": True
                },
                {
                    "product_id": basic_sample_data["product2_id"],
                    "shipping_location_id": basic_sample_data["shipping_location_id"],
                    "ship_to_billing_address": False
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == basic_sample_data["customer_id"]
        assert data["total_cost"] == 3000  # 1000 + 2000
        
        # Verify both purchase products were created
        from src.data.tables.purchase_product import PurchaseProduct
        db = test_db()
        purchase_products = db.query(PurchaseProduct).filter(
            PurchaseProduct.purchase_rollup_id == data["id"]
        ).all()
        assert len(purchase_products) == 2
        db.close()
    
    def test_create_purchase_invalid_customer(self, client):
        """Test purchase creation with non-existent customer"""
        purchase_data = {
            "customer_id": 99999,
            "products": [
                {
                    "product_id": 1,
                    "ship_to_billing_address": True
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        assert response.status_code == 400
        assert "Customer with id 99999 not found" in response.json()["detail"]
    
    def test_create_purchase_invalid_product(self, client, basic_sample_data):
        """Test purchase creation with non-existent product"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": 99999,
                    "ship_to_billing_address": True
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        assert response.status_code == 400
        assert "Product with id 99999 not found" in response.json()["detail"]
    
    def test_create_purchase_invalid_location(self, client, basic_sample_data):
        """Test purchase creation with non-existent shipping location"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "shipping_location_id": 99999,
                    "ship_to_billing_address": False
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        assert response.status_code == 400
        assert "Location with id 99999 not found" in response.json()["detail"]
    
    def test_get_purchase_by_id_success(self, client, basic_sample_data):
        """Test successful purchase retrieval"""
        # First create a purchase
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "ship_to_billing_address": True
                }
            ]
        }
        
        create_response = client.post("/purchase/", json=purchase_data)
        assert create_response.status_code == 200
        purchase_id = create_response.json()["id"]
        
        # Now retrieve the purchase
        response = client.get(f"/purchase/{purchase_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == purchase_id
        assert data["customer_id"] == basic_sample_data["customer_id"]
        assert data["total_cost"] == 1000
    
    def test_get_purchase_by_id_not_found(self, client):
        """Test purchase retrieval with non-existent ID"""
        response = client.get("/purchase/99999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Purchase not found"
    
    def test_create_purchase_validation_no_shipping_option(self, client, basic_sample_data):
        """Test purchase creation validation when no shipping option is specified"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "ship_to_billing_address": False
                    # No shipping_location or shipping_location_id provided
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_purchase_validation_multiple_shipping_options(self, client, basic_sample_data):
        """Test purchase creation validation when multiple shipping options are specified"""
        purchase_data = {
            "customer_id": basic_sample_data["customer_id"],
            "products": [
                {
                    "product_id": basic_sample_data["product1_id"],
                    "ship_to_billing_address": True,
                    "shipping_location_id": basic_sample_data["shipping_location_id"]
                    # Both billing and location ID specified
                }
            ]
        }
        
        response = client.post("/purchase/", json=purchase_data)
        assert response.status_code == 422  # Validation error