import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("prepare_database")
class TestNoToken:
    def test_list_orders_unauthorized(self, client: TestClient):
        response = client.get("/orders/")
        assert response.status_code == 401

    def test_get_order_unauthorized(self, client: TestClient, create_test_order):
        response = client.get(f"/orders/{create_test_order.id}")
        assert response.status_code == 401

    def test_create_order_unauthorized(
        self, client: TestClient, create_test_client, create_test_product
    ):
        payload = {
            "client_id": create_test_client.id,
            "status": "pending",
            "products": [{"product_id": create_test_product.id, "quantity": 1}],
        }
        response = client.post("/orders/", json=payload)
        assert response.status_code == 401

    def test_update_order_unauthorized(
        self, client: TestClient, create_test_order, create_test_product
    ):
        payload = {
            "status": "confirmed",
            "products": [
                {
                    "id": create_test_order.products[0].id,
                    "product_id": create_test_product.id,
                    "quantity": 2,
                }
            ],
        }
        response = client.put(f"/orders/{create_test_order.id}", json=payload)
        assert response.status_code == 401

    def test_delete_order_unauthorized(self, client: TestClient, create_test_order):
        response = client.delete(f"/orders/{create_test_order.id}")
        assert response.status_code == 401


@pytest.mark.usefixtures("prepare_database")
class TestUserToken:
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_user):
        self.headers = {"Authorization": f"Bearer {token_user}"}

    def test_list_orders_user_allowed(self, client: TestClient):
        response = client.get("/orders/", headers=self.headers)
        assert response.status_code == 200

    def test_get_order_user_allowed(self, client: TestClient, create_test_order):
        response = client.get(f"/orders/{create_test_order.id}", headers=self.headers)
        assert response.status_code == 200

    def test_create_order_user_allowed(
        self, client: TestClient, create_test_client, create_test_product
    ):
        payload = {
            "client_id": create_test_client.id,
            "status": "pending",
            "products": [{"product_id": create_test_product.id, "quantity": 1}],
        }
        response = client.post("/orders/", json=payload, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == create_test_client.id
        assert data["status"] == "pending"

    def test_update_order_user_allowed(
        self, client: TestClient, create_test_order, create_test_product
    ):
        payload = {
            "status": "confirmed",
            "products": [
                {
                    "id": create_test_order.products[0].id,
                    "product_id": create_test_product.id,
                    "quantity": 3,
                }
            ],
        }
        response = client.put(
            f"/orders/{create_test_order.id}", json=payload, headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["products"][0]["quantity"] == 3

    def test_delete_order_user_allowed(self, client: TestClient, create_test_order):
        response = client.delete(
            f"/orders/{create_test_order.id}", headers=self.headers
        )
        assert response.status_code == 200

        # Confirm delete
        get_response = client.get(
            f"/orders/{create_test_order.id}", headers=self.headers
        )
        assert get_response.status_code == 404


@pytest.mark.usefixtures("prepare_database")
class TestAdminTokenAccess:
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_admin):
        self.headers = {"Authorization": f"Bearer {token_admin}"}

    def test_list_orders_admin_allowed(self, client: TestClient):
        response = client.get("/orders/", headers=self.headers)
        assert response.status_code == 200

    def test_get_order_admin_allowed(self, client: TestClient, create_test_order):
        response = client.get(f"/orders/{create_test_order.id}", headers=self.headers)
        assert response.status_code == 200

    def test_create_order_admin_allowed(
        self, client: TestClient, create_test_client, create_test_product
    ):
        payload = {
            "client_id": create_test_client.id,
            "status": "pending",
            "products": [{"product_id": create_test_product.id, "quantity": 1}],
        }
        response = client.post("/orders/", json=payload, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == create_test_client.id

    def test_update_order_admin_allowed(
        self, client: TestClient, create_test_order, create_test_product
    ):
        payload = {
            "status": "shipped",
            "products": [
                {
                    "id": create_test_order.products[0].id,
                    "product_id": create_test_product.id,
                    "quantity": 5,
                }
            ],
        }
        response = client.put(
            f"/orders/{create_test_order.id}", json=payload, headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "shipped"
        assert data["products"][0]["quantity"] == 5

    def test_delete_order_admin_allowed(self, client: TestClient, create_test_order):
        response = client.delete(
            f"/orders/{create_test_order.id}", headers=self.headers
        )
        assert response.status_code == 200

        # Confirm delete
        get_response = client.get(
            f"/orders/{create_test_order.id}", headers=self.headers
        )
        assert get_response.status_code == 404
