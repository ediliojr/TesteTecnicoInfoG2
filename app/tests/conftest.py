import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.models import User, Client
from app.core.security import hash_password
from app.models.order_model import Order, OrderProduct
from app.models.product_model import Product
from app.utils.jwt import create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Remove arquivo se existir para garantir banco limpo
if os.path.exists("test.db"):
    os.remove("test.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    admin_user = User(
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        is_admin=1,
        is_active=1,
    )
    regular_user = User(
        email="user@test.com",
        hashed_password=hash_password("user123"),
        is_admin=0,
        is_active=1,
    )
    db.add_all([admin_user, regular_user])
    db.commit()
    db.close()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def token_admin():
    return create_access_token({"sub": "admin@test.com", "is_admin": True})


@pytest.fixture()
def token_user():
    return create_access_token({"sub": "user@test.com", "is_admin": False})


@pytest.fixture()
def create_test_client():
    db = TestingSessionLocal()
    unique_email = f"{uuid.uuid4()}@test.com"
    client = Client(
        name="Test Client",
        email=unique_email,
        cpf=str(uuid.uuid4().int)[:11],
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    db.close()
    return client


@pytest.fixture()
def create_test_product():
    db = TestingSessionLocal()
    product = Product(
        description="Produto Teste",
        price=49.99,
        barcode=str(uuid.uuid4().int)[:13],
        section="Roupas",
        stock=10,
        image_path="tests/assets/test_image.gif",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    db.close()
    return product


@pytest.fixture
def create_second_client(client, token_admin):
    headers = {"Authorization": f"Bearer {token_admin}"}
    payload = {
        "name": "Second Client",
        "email": f"{uuid.uuid4().hex[:6]}@example.com",
        "cpf": str(uuid.uuid4().int)[:11],
    }
    response = client.post("/clients/", json=payload, headers=headers)
    assert response.status_code == 200
    return response.json()


@pytest.fixture()
def create_test_order(create_test_client, create_test_product, create_test_user):
    db = TestingSessionLocal()

    # Cria o pedido para o cliente e atribui o usuário que criou
    order = Order(
        client_id=create_test_client.id,
        status="pending",
        created_by=create_test_user.id,  # aqui o created_by
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Adiciona o produto ao pedido
    order_product = OrderProduct(
        order_id=order.id,
        product_id=create_test_product.id,
        quantity=2,
    )
    db.add(order_product)
    db.commit()
    db.refresh(order_product)

    # Força o carregamento dos produtos para evitar lazy loading fora da sessão
    _ = order.products

    db.expunge(order)
    db.close()

    return order


@pytest.fixture()
def create_test_user():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "user@test.com").first()
    db.close()
    return user
