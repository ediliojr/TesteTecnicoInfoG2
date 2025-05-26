from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.validations.client_validation import validate_unique_email, validate_unique_cpf


# Pesquisa todos os clientes com filtro e paginação
def get_clients(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> List[Client]:
    query = db.query(Client)
    if name:
        query = query.filter(Client.name.contains(name))
    if email:
        query = query.filter(Client.email.contains(email))
    return query.offset(skip).limit(limit).all()


# Procura um cliente por ID
def get_client_by_id(db: Session, client_id: int) -> Client | None:
    return db.get(Client, client_id)


# Cria um novo cliente
def create_client(db: Session, client_data: ClientCreate) -> Client:

    # Validaçoes
    validate_unique_email(db, client_data.email)
    validate_unique_cpf(db, client_data.cpf)

    client = Client(**client_data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


# Atualiza um cliente por ID
def update_client(db: Session, client_id: int, update_data: ClientUpdate) -> Client:
    client = db.get(Client, client_id)
    if not client:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)

    # Validações
    validate_unique_email(db, update_dict.get("email"), client_id=client.id)
    validate_unique_cpf(db, update_dict.get("cpf"), client_id=client.id)

    for field, value in update_dict.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


# Deleta um cliente por ID
def delete_client(db: Session, client_id: int) -> bool:
    client = db.get(Client, client_id)
    if not client:
        return False
    db.delete(client)
    db.commit()
    return True
