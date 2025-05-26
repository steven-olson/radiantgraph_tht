from fastapi.testclient import TestClient
from src.main import app
import pytest


client = TestClient(app)


def test_ping():
    response = client.get("/")
    assert response.status_code == 200
    assert bool(response.json())


if __name__ == "__main__":
    pytest.main(["./test_main.py", "-v"])