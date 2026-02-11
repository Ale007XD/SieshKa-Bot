from fastapi.testclient import TestClient
from app.main import app

def test_shop_home_exists():
    with TestClient(app) as client:
        r = client.get('/shop/index.html')
        assert r.status_code in (200, 304, 302)

def test_menu_endpoints_accessible():
    with TestClient(app) as client:
        r1 = client.get('/api/v1/menu/categories')
        r2 = client.get('/api/v1/menu/products')
        assert r1.status_code in (200, 422)
        assert r2.status_code in (200, 422)

def test_guest_order_flow():
    with TestClient(app) as client:
        payload = {
            "name": "Test User",
            "phone": "+10000000000",
            "address": "Test Address",
            "items": [{"product_id": "burger", "quantity": 1}],
            "notes": ""
        }
        r = client.post('/api/v1/orders/guest', json=payload)
        assert r.status_code == 201
