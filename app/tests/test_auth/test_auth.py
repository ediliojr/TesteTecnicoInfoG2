from app.utils.helpers import generate_unique_email

CLIENT_PASSWORD = "senha123"


# Teste de autenticação
class TestAuth:
    # Registro
    def test_register_allowed(self, client):
        email = generate_unique_email()
        response = client.post(
            "/auth/register", json={"email": email, "password": CLIENT_PASSWORD}
        )
        assert response.status_code == 200
        assert response.json()["email"] == email

    # Registro duplicado
    def test_register_duplicate_email_forbidden(self, client):
        email = generate_unique_email()

        # Primeiro registro
        client.post(
            "/auth/register", json={"email": email, "password": CLIENT_PASSWORD}
        )

        # Segundo registro
        response = client.post(
            "/auth/register", json={"email": email, "password": CLIENT_PASSWORD}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Email is already in use"

    # Login com credenciais corretas
    def test_login_success_allowed(self, client):
        email = generate_unique_email()

        client.post(
            "/auth/register", json={"email": email, "password": CLIENT_PASSWORD}
        )
        response = client.post(
            "/auth/login", data={"username": email, "password": CLIENT_PASSWORD}
        )

        assert response.status_code == 200
        json_data = response.json()
        assert "access_token" in json_data
        assert "refresh_token" in json_data
        assert json_data["token_type"] == "bearer"

    # Login com credenciais erradas
    def test_login_invalid_credentials_forbidden(self, client):
        response = client.post(
            "/auth/login", data={"username": "wrong@test.com", "password": "wrongpass"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    # Refresh token
    def test_refresh_token_allowed(self, client):
        email = generate_unique_email()

        # Faz o regristro e login para gerar o token a ser usado
        client.post(
            "/auth/register", json={"email": email, "password": CLIENT_PASSWORD}
        )
        login_response = client.post(
            "/auth/login", data={"username": email, "password": CLIENT_PASSWORD}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = client.post("/auth/refresh", json=refresh_token)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    # Refresh token invalido
    def test_refresh_token_invalid_forbidden(self, client):
        response = client.post("/auth/refresh", json="invalid.token.here")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"

    # Deleta o usuario autenticado
    def test_delete_user_authenticated_allowed(self, client):
        email = generate_unique_email()

        # Faz o regristro e login
        client.post(
            "/auth/register", json={"email": email, "password": CLIENT_PASSWORD}
        )
        login_response = client.post(
            "/auth/login", data={"username": email, "password": CLIENT_PASSWORD}
        )
        access_token = login_response.json()["access_token"]

        # Deleta o usuario
        response = client.delete(
            "/auth/delete", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 204

    # Deleta o usuario não autenticado
    def test_delete_user_unauthenticated(self, client):
        response = client.delete("/auth/delete")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
