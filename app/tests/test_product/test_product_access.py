import pytest

PRODUCT_SAMPLE = {
    "description": "Produto Teste",
    "price": 49.99,
    "barcode": "1234567890123",
    "section": "Roupas",
    "stock": 10,
    "image_base64": "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",
}


# Testes sem autenticação
class TestNoToken:
    # Área permitida a user/admin
    def test_list_products_user_allowed(self, client):
        response = client.get("/products/")
        assert response.status_code == 401

    def test_get_product_user_allowed(self, client, create_test_product):
        response = client.get(f"/products/{create_test_product.id}")
        assert response.status_code == 401

    # Área permitida a admin
    def test_create_product_user_forbidden(self, client):
        response = client.post("/products/", json=PRODUCT_SAMPLE)
        assert response.status_code == 401

    def test_update_product_user_forbidden(self, client, create_test_product):
        response = client.put(
            f"/products/{create_test_product.id}", json={"price": 59.99}
        )
        assert response.status_code == 401

    def test_delete_product_user_forbidden(self, client, create_test_product):
        response = client.delete(f"/products/{create_test_product.id}")
        assert response.status_code == 401


# Teste com autenticação user
class TestUserToken:
    # Setup
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_user):
        self.headers = {"Authorization": f"Bearer {token_user}"}

    # Área permitida a user/admin
    def test_list_products_user_allowed(self, client):
        response = client.get("/products/", headers=self.headers)
        assert response.status_code == 200

    def test_get_product_user_allowed(self, client, create_test_product):
        response = client.get(
            f"/products/{create_test_product.id}", headers=self.headers
        )
        assert response.status_code == 200

    # Área permitida a admin
    def test_create_product_user_forbidden(self, client):
        response = client.post("/products/", json=PRODUCT_SAMPLE, headers=self.headers)
        assert response.status_code == 403

    def test_update_product_user_forbidden(self, client, create_test_product):
        response = client.put(
            f"/products/{create_test_product.id}",
            json={"price": 59.99},
            headers=self.headers,
        )
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
        assert response.status_code == 403

    def test_delete_product_user_forbidden(self, client, create_test_product):
        response = client.delete(
            f"/products/{create_test_product.id}", headers=self.headers
        )
        assert response.status_code == 403


# Testes com autenticação Admin
class TestAdminTokenAccess:
    # Setup
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_admin):
        self.headers = {"Authorization": f"Bearer {token_admin}"}

    # Área permitida a user/admin
    def test_list_products_admin_allowed(self, client):
        response = client.get("/products/", headers=self.headers)
        assert response.status_code == 200

    def test_get_product_admin_allowed(self, client, create_test_product):
        response = client.get(
            f"/products/{create_test_product.id}", headers=self.headers
        )
        assert response.status_code == 200

    # Área permitida a admin
    def test_create_product_admin_allowed(self, client):
        response = client.post("/products/", json=PRODUCT_SAMPLE, headers=self.headers)
        assert response.status_code == 200
        assert response.json()["description"] == PRODUCT_SAMPLE["description"]

    def test_update_product_admin_allowed(self, client, create_test_product):
        response = client.put(
            f"/products/{create_test_product.id}",
            json={"price": 59.99},
            headers=self.headers,
        )
        assert response.status_code == 200
        assert response.json()["price"] == 59.99

    def test_delete_product_admin_allowed(self, client, create_test_product):
        response = client.delete(
            f"/products/{create_test_product.id}", headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Product deleted successfully"
