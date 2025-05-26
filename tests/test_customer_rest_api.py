import pytest
from fastapi.testclient import TestClient
from src.data.tables.customer import Customer
from src.data.tables.location import Location


class TestCustomerEndpoints:
    
    def test_create_customer_success(self, client, test_db):
        """Test successful customer creation"""
        customer_data = {
            "email": "test@example.com",
            "phone_number": "1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "billing_address": {
                "location_type": "billing",
                "address_line_1": "123 Main St",
                "address_line_2": "Apt 1",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            }
        }
        
        response = client.post("/customer/", json=customer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["phone_number"] == "1234567890"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert "id" in data
        assert "billing_location_id" in data
        
        # Verify data was persisted in database
        db = test_db()
        customer = db.query(Customer).filter(Customer.email == "test@example.com").first()
        assert customer is not None
        assert customer.phone_number == "1234567890"
        
        # Verify billing location was created
        location = db.query(Location).filter(Location.id == customer.billing_location_id).first()
        assert location is not None
        assert location.address_line_1 == "123 Main St"
        assert location.city == "Anytown"
        db.close()
    
    def test_get_customer_by_phone_success(self, client):
        """Test successful customer retrieval by phone"""
        # First create a customer
        customer_data = {
            "email": "phone@example.com",
            "phone_number": "5551234567",
            "first_name": "Jane",
            "last_name": "Smith",
            "billing_address": {
                "location_type": "billing",
                "address_line_1": "456 Oak Ave",
                "city": "Somewhere",
                "state": "TX",
                "zip_code": "54321"
            }
        }
        
        create_response = client.post("/customer/", json=customer_data)
        assert create_response.status_code == 200
        
        # Now retrieve by phone
        response = client.get("/customer/by-phone/5551234567")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "phone@example.com"
        assert data["phone_number"] == "5551234567"
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
    
    def test_get_customer_by_phone_not_found(self, client):
        """Test customer retrieval by non-existent phone"""
        response = client.get("/customer/by-phone/9999999999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found"
    
    def test_get_customer_by_email_success(self, client):
        """Test successful customer retrieval by email"""
        # First create a customer
        customer_data = {
            "email": "email@example.com",
            "phone_number": "5559876543",
            "first_name": "Bob",
            "last_name": "Johnson",
            "billing_address": {
                "location_type": "billing",
                "address_line_1": "789 Pine St",
                "city": "Elsewhere",
                "state": "NY",
                "zip_code": "67890"
            }
        }
        
        create_response = client.post("/customer/", json=customer_data)
        assert create_response.status_code == 200
        
        # Now retrieve by email
        response = client.get("/customer/by-email/email@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "email@example.com"
        assert data["phone_number"] == "5559876543"
        assert data["first_name"] == "Bob"
        assert data["last_name"] == "Johnson"
    
    def test_get_customer_by_email_not_found(self, client):
        """Test customer retrieval by non-existent email"""
        response = client.get("/customer/by-email/nonexistent@example.com")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found"
    
    def test_create_customer_invalid_email(self, client):
        """Test customer creation with invalid email format"""
        customer_data = {
            "email": "invalid-email",
            "phone_number": "1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "billing_address": {
                "location_type": "billing",
                "address_line_1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            }
        }
        
        response = client.post("/customer/", json=customer_data)
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main(["./test_customer_rest_api.py", "-v"])
