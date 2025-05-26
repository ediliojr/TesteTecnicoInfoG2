import pytest
import uuid

CLIENT_SAMPLE = {
    "name": "Test Client",
    "email": "client@example.com",
    "cpf": "12345678900",
}


class TestClientBusinessRules:
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_admin):
        self.headers = {"Authorization": f"Bearer {token_admin}"}

    def unique_client_payload(self):
        return {
            "name": f"Client {uuid.uuid4().hex[:4]}",
            "email": f"{uuid.uuid4().hex[:6]}@example.com",
            "cpf": str(uuid.uuid4().int)[:11],
        }

    def test_create_valid_client(self, client):
        payload = self.unique_client_payload()
        response = client.post("/clients/", json=payload, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["email"] == payload["email"]
        assert data["cpf"] == payload["cpf"]

    def test_create_client_with_duplicate_email(self, client, create_test_client):
        payload = self.unique_client_payload()
        payload["email"] = create_test_client.email

        response = client.post("/clients/", json=payload, headers=self.headers)
        assert response.status_code == 400

    def test_create_client_with_duplicate_cpf(self, client, create_test_client):
        payload = self.unique_client_payload()
        payload["cpf"] = create_test_client.cpf

        response = client.post("/clients/", json=payload, headers=self.headers)
        assert response.status_code == 400

    def test_create_client_missing_fields(self, client):
        payload = {"name": "No Email or CPF"}
        response = client.post("/clients/", json=payload, headers=self.headers)
        assert response.status_code == 422

    def test_update_client_name(self, client, create_test_client):
        response = client.put(
            f"/clients/{create_test_client.id}",
            json={"name": "Updated Name"},
            headers=self.headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_client_duplicate_email(
        self, client, create_test_client, create_second_client
    ):
        response = client.put(
            f"/clients/{create_test_client.id}",
            json={"email": create_second_client["email"]},
            headers=self.headers,
        )
        assert response.status_code == 400

    def test_update_client_duplicate_cpf(
        self, client, create_test_client, create_second_client
    ):
        response = client.put(
            f"/clients/{create_test_client.id}",
            json={"cpf": create_second_client["cpf"]},
            headers=self.headers,
        )
        assert response.status_code == 400

    def test_get_client_by_id(self, client, create_test_client):
        response = client.get(f"/clients/{create_test_client.id}", headers=self.headers)
        assert response.status_code == 200
        assert response.json()["id"] == create_test_client.id

    def test_list_clients(self, client):
        response = client.get("/clients/", headers=self.headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_client(self, client, create_test_client):
        response = client.delete(
            f"/clients/{create_test_client.id}", headers=self.headers
        )
        assert response.status_code == 200

        # Confirma que foi deletado
        follow_up = client.get(
            f"/clients/{create_test_client.id}", headers=self.headers
        )
        assert follow_up.status_code == 404
