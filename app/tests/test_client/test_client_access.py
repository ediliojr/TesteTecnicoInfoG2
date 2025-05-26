import pytest

CLIENT_SAMPLE = {
    "name": "Test Client",
    "email": "client@example.com",
    "cpf": "12345678900",
}


# Testes sem autenticação
class TestNoToken:
    # Area permitida a user/admin
    def test_list_clients_user_allowed(self, client):
        response = client.get("/clients/")
        assert response.status_code == 401

    def test_get_client_user_allowed(self, client, create_test_client):
        response = client.get(f"/clients/{create_test_client.id}")
        assert response.status_code == 401

    # Area permitida a admin
    def test_create_client_user_forbidden(self, client):
        response = client.post("/clients/", json=CLIENT_SAMPLE)
        assert response.status_code == 401

    def test_update_client_user_forbidden(self, client, create_test_client):
        response = client.put(
            f"/clients/{create_test_client.id}", json={"name": "New Name"}
        )
        assert response.status_code == 401

    def test_delete_client_user_forbidden(self, client, create_test_client):
        response = client.delete(f"/clients/{create_test_client.id}")
        assert response.status_code == 401


# Teste com autenticação user
class TestUserToken:
    # Setup
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_user):
        self.headers = {"Authorization": f"Bearer {token_user}"}

    # Area permitida a user/admin
    def test_list_clients_user_allowed(self, client):
        response = client.get("/clients/", headers=self.headers)
        assert response.status_code == 200

    def test_get_client_user_allowed(self, client, create_test_client):
        response = client.get(f"/clients/{create_test_client.id}", headers=self.headers)
        assert response.status_code == 200

    # Area permitida a admin
    def test_create_client_user_forbidden(self, client):
        response = client.post("/clients/", json=CLIENT_SAMPLE, headers=self.headers)
        assert response.status_code == 403

    def test_update_client_user_forbidden(self, client, create_test_client):
        response = client.put(
            f"/clients/{create_test_client.id}",
            json={"name": "New Name"},
            headers=self.headers,
        )
        assert response.status_code == 403

    def test_delete_client_user_forbidden(self, client, create_test_client):
        response = client.delete(
            f"/clients/{create_test_client.id}", headers=self.headers
        )
        assert response.status_code == 403


# Testes com autenticaçao Admin
class TestAdminTokenAccess:
    # Setup
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_admin):
        self.headers = {"Authorization": f"Bearer {token_admin}"}

    # Area permitida a user/admin
    def test_list_clients_admin_allowed(self, client):
        response = client.get("/clients/", headers=self.headers)
        assert response.status_code == 200

    def test_get_client_admin_allowed(self, client, create_test_client):
        response = client.get(f"/clients/{create_test_client.id}", headers=self.headers)
        assert response.status_code == 200

    # Area permitida a admin
    def test_create_client_admin_allowed(self, client):
        response = client.post("/clients/", json=CLIENT_SAMPLE, headers=self.headers)
        assert response.status_code == 200

    def test_update_client_admin_allowed(self, client, create_test_client):
        response = client.put(
            f"/clients/{create_test_client.id}",
            json={"name": "New Name"},
            headers=self.headers,
        )
        assert response.status_code == 200

    def test_delete_client_admin_allowed(self, client, create_test_client):
        response = client.delete(
            f"/clients/{create_test_client.id}", headers=self.headers
        )
        assert response.status_code == 200
