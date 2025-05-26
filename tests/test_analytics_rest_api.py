import pytest
from fastapi.testclient import TestClient


class TestAnalyticsEndpoints:
    
    def test_orders_by_billing_zip_descending(self, client, analytics_sample_data):
        """Test billing zip analytics with descending order (default)"""
        response = client.get("/analytics/orders-by-billing-zip")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # Two different billing zip codes
        
        # Should be sorted descending by order count
        # Zip 12345 has 4 orders (customer 1 has 3 orders + customer 3 has 1 order), zip 54321 has 1 order (customer 2)
        assert data[0]["zip_code"] == "12345"
        assert data[0]["order_count"] == 4
        assert data[1]["zip_code"] == "54321"
        assert data[1]["order_count"] == 1
    
    def test_orders_by_billing_zip_ascending(self, client, analytics_sample_data):
        """Test billing zip analytics with ascending order"""
        response = client.get("/analytics/orders-by-billing-zip?ascending=true")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Should be sorted ascending by order count
        assert data[0]["zip_code"] == "54321"
        assert data[0]["order_count"] == 1
        assert data[1]["zip_code"] == "12345"
        assert data[1]["order_count"] == 4
    
    def test_orders_by_shipping_zip_descending(self, client, analytics_sample_data):
        """Test shipping zip analytics with descending order (default)"""
        response = client.get("/analytics/orders-by-shipping-zip")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should include shipping and store locations
        zip_codes = [item["zip_code"] for item in data]
        order_counts = [item["order_count"] for item in data]
        
        # Verify we have the expected zip codes
        assert "78901" in zip_codes  # shipping_location_1
        assert "55555" in zip_codes  # store_location_1
        
        # Should be sorted descending by order count
        assert order_counts == sorted(order_counts, reverse=True)
    
    def test_orders_by_shipping_zip_ascending(self, client, analytics_sample_data):
        """Test shipping zip analytics with ascending order"""
        response = client.get("/analytics/orders-by-shipping-zip?ascending=true")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        order_counts = [item["order_count"] for item in data]
        # Should be sorted ascending by order count
        assert order_counts == sorted(order_counts)
    
    def test_store_purchase_times(self, client, analytics_sample_data):
        """Test store purchase times analytics"""
        response = client.get("/analytics/store-purchase-times")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should only include store purchases
        # We have store purchases at hours 11 (2 purchases) and 15 (1 purchase)
        hours = [item["hour"] for item in data]
        counts = [item["purchase_count"] for item in data]
        
        assert 11 in hours
        assert 15 in hours
        
        # Find the 11 AM entry (should have 2 purchases)
        hour_11_data = next(item for item in data if item["hour"] == 11)
        assert hour_11_data["purchase_count"] == 2
        
        # Should be sorted descending by purchase count
        assert counts == sorted(counts, reverse=True)
    
    def test_top_store_pickup_users(self, client, analytics_sample_data):
        """Test top store pickup users analytics"""
        response = client.get("/analytics/top-store-pickup-users")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Customer 1 should be at the top with 2 store orders
        # (purchase_rollup_id 2 and 5 both have store pickups)
        assert len(data) >= 1
        top_user = data[0]
        
        assert "customer_id" in top_user
        assert "first_name" in top_user
        assert "last_name" in top_user
        assert "email" in top_user
        assert "store_order_count" in top_user
        
        # Customer 1 should have the most store orders
        assert top_user["customer_id"] == analytics_sample_data["customer_1_id"]
        assert top_user["first_name"] == "John"
        assert top_user["last_name"] == "Doe"
        assert top_user["store_order_count"] == 2
    
    def test_analytics_endpoints_empty_data(self, client):
        """Test analytics endpoints with no data"""
        # Test all endpoints return empty lists when no data exists
        
        response = client.get("/analytics/orders-by-billing-zip")
        assert response.status_code == 200
        assert response.json() == []
        
        response = client.get("/analytics/orders-by-shipping-zip")
        assert response.status_code == 200
        assert response.json() == []
        
        response = client.get("/analytics/store-purchase-times")
        assert response.status_code == 200
        assert response.json() == []
        
        response = client.get("/analytics/top-store-pickup-users")
        assert response.status_code == 200
        assert response.json() == []