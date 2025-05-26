import pytest


@pytest.fixture
def admin_headers(token_admin):
    return {"Authorization": f"Bearer {token_admin}"}


class TestAdminOrderBusinessRules:

    def test_delete_nonexistent_order_should_return_404(self, client, admin_headers):
        response = client.delete(
            "/orders/999999", headers=admin_headers
        )  # id que não existe
        assert response.status_code == 404  # pedido não encontrado

    def test_get_nonexistent_order_should_return_404(self, client, admin_headers):
        response = client.get("/orders/999999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_nonexistent_order_should_return_404(self, client, admin_headers):
        update_data = {"status": "shipped"}
        response = client.put("/orders/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
