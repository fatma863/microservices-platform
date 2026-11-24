import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add service paths to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "services" / "auth_service"))
sys.path.append(str(BASE_DIR / "services" / "catalog_service"))

from services.auth_service.main import app as auth_app
from services.catalog_service.main import app as catalog_app

client_auth = TestClient(auth_app)
client_catalog = TestClient(catalog_app)

def test_auth_health():
    response = client_auth.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_register_and_login():
    reg_payload = {"username": "cloudengineer", "password": "securepassword123", "email": "cloud@example.com"}
    reg_res = client_auth.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    login_payload = {"username": "cloudengineer", "password": "securepassword123"}
    login_res = client_auth.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    verify_res = client_auth.get("/api/v1/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert verify_res.status_code == 200
    assert verify_res.json()["username"] == "cloudengineer"

def test_catalog_health():
    response = client_catalog.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "catalog-service"

def test_catalog_list_and_filter():
    response = client_catalog.get("/api/v1/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 4

    compute_res = client_catalog.get("/api/v1/products?category=Compute")
    assert compute_res.status_code == 200
    for prod in compute_res.json():
        assert prod["category"] == "Compute"

