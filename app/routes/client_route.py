from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.client_schema import ClientCreate, ClientOut, ClientUpdate
from app.db.database import get_db
from app.routes.auth_route import get_current_user, require_admin
from app.services.client_service import (
    get_clients as service_get_clients,
    get_client_by_id,
    create_client as service_create_client,
    update_client as service_update_client,
    delete_client as service_delete_client,
)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get(
    "/",
    response_model=List[ClientOut],
    summary="Listar clientes",
    description=(
        "Lista todos os clientes cadastrados com suporte a paginação e filtros.\n\n"
        "Regras de negócio:\n"
        "- Suporta filtros por nome e email para facilitar a busca.\n"
        "- Paginação controlada pelos parâmetros 'skip' e 'limit'.\n\n"
        "Casos de uso:\n"
        "- Visualizar clientes para administração ou consulta."
    ),
)
def get_clients(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    return service_get_clients(db, skip, limit, name, email)


@router.post(
    "/",
    response_model=ClientOut,
    summary="Criar cliente",
    description=(
        "Cria um novo cliente no sistema.\n\n"
        "Regras de negócio:\n"
        "- O email e o CPF devem ser únicos.\n"
        "- Apenas usuários com perfil admin podem criar clientes.\n\n"
        "Casos de uso:\n"
        "- Cadastro de novos clientes para uso no sistema."
    ),
)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return service_create_client(db, client)


@router.get(
    "/{client_id}",
    response_model=ClientOut,
    summary="Obter cliente por ID",
    description=(
        "Obtém detalhes de um cliente específico pelo seu ID.\n\n"
        "Regras de negócio:\n"
        "- Retorna erro 404 se o cliente não for encontrado.\n\n"
        "Casos de uso:\n"
        "- Consultar dados completos de um cliente."
    ),
)
def get_client(
    client_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    client = get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.put(
    "/{client_id}",
    response_model=ClientOut,
    summary="Atualizar cliente",
    description=(
        "Atualiza os dados de um cliente existente.\n\n"
        "Regras de negócio:\n"
        "- Apenas usuários admin podem realizar atualização.\n"
        "- Retorna erro 404 se o cliente não existir.\n\n"
        "Casos de uso:\n"
        "- Corrigir ou modificar informações do cliente."
    ),
)
def update_client(
    client_id: int,
    update_data: ClientUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    client = service_update_client(db, client_id, update_data)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.delete(
    "/{client_id}",
    summary="Deletar cliente",
    description=(
        "Remove um cliente do sistema.\n\n"
        "Regras de negócio:\n"
        "- Apenas usuários admin podem deletar clientes.\n"
        "- Retorna erro 404 se o cliente não existir.\n\n"
        "Casos de uso:\n"
        "- Exclusão definitiva de cliente."
    ),
)
def delete_client(
    client_id: int, db: Session = Depends(get_db), user=Depends(require_admin)
):
    success = service_delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"detail": "Cliente deletado com sucesso"}
