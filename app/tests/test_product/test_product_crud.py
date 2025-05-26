import pytest

VALID_IMAGE = (
    "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
)

INVALID_PRODUCTS = [
    {
        "description": "",
        "price": 10.0,
        "barcode": "0000000000001",
        "section": "Roupas",
        "stock": 5,
        "image_base64": VALID_IMAGE,
    },
    {
        "description": "Teste",
        "price": -5.0,
        "barcode": "0000000000002",
        "section": "Roupas",
        "stock": 5,
        "image_base64": VALID_IMAGE,
    },
    {
        "description": "Teste",
        "price": 10.0,
        "barcode": "",
        "section": "Roupas",
        "stock": 5,
        "image_base64": VALID_IMAGE,
    },
    {
        "description": "Teste",
        "price": 10.0,
        "barcode": "0000000000003",
        "section": "Roupas",
        "stock": -1,
        "image_base64": VALID_IMAGE,
    },
]


class TestAdminCrudValidations:
    @pytest.fixture(autouse=True)
    def setup_headers(self, token_admin):
        self.headers = {"Authorization": f"Bearer {token_admin}"}

    def test_create_product_with_invalid_data(self, client):
        for invalid_product in INVALID_PRODUCTS:
            response = client.post(
                "/products/", json=invalid_product, headers=self.headers
            )
            assert response.status_code == 422

    def test_create_product_duplicate_barcode(self, client, create_test_product):
        product_data = {
            "description": "Outro Produto",
            "price": 20.0,
            "barcode": create_test_product.barcode,
            "section": "Eletrônicos",
            "stock": 10,
            "image_base64": "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",
        }
        response = client.post("/products/", json=product_data, headers=self.headers)
        assert response.status_code == 400
        assert "barcode" in response.json()["detail"].lower()

    def test_update_product_with_invalid_data(self, client, create_test_product):
        test_cases = [
            {"price": -10},
            {"description": ""},
            {"stock": -5},
            {"barcode": ""},
        ]
        for invalid_data in test_cases:
            response = client.put(
                f"/products/{create_test_product.id}",
                json=invalid_data,
                headers=self.headers,
            )
            # Debug em caso de erro
            print("\n[TEST CASE] Enviando:", invalid_data)
            print("Status:", response.status_code)
            print("Resposta:", response.json())
            assert (
                response.status_code == 422
            ), f"Esperado 422, mas recebeu {response.status_code} para input {invalid_data}"

    def test_update_product_duplicate_barcode(self, client, create_test_product):
        product_data = {
            "description": "Produto Extra",
            "price": 15.0,
            "barcode": "9999999999999",
            "section": "Roupas",
            "stock": 8,
            "image_base64": "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",
        }
        res = client.post("/products/", json=product_data, headers=self.headers)
        assert res.status_code == 200
        new_product_id = res.json()["id"]

        response = client.put(
            f"/products/{new_product_id}",
            json={"barcode": create_test_product.barcode},
            headers=self.headers,
        )
        print("\n[UPDATE DUPLICATE] Status:", response.status_code)
        print("Resposta:", response.json())
        assert response.status_code == 400
        assert "barcode" in response.json()["detail"].lower()

    def test_delete_nonexistent_product_returns_404(self, client):
        response = client.delete("/products/9999999", headers=self.headers)
        assert response.status_code == 404
