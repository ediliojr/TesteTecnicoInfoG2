from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.user_model import User
from app.schemas.order_schema import OrderCreate, OrderOut, OrderUpdate
from app.db.database import get_db
from app.services.order_service import (
    create_order,
    get_order,
    list_orders,
    update_order,
    delete_order,
)
from app.routes.auth_route import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
    description=(
        "Cria um novo pedido no sistema.\n\n"
        "Regras de negócio:\n"
        "- O pedido é sempre associado ao usuário autenticado que o criou.\n"
        "- O campo `client_id` deve referenciar um cliente válido.\n"
        "- O pedido pode conter múltiplos produtos com quantidades específicas.\n\n"
        "Casos de uso:\n"
        "- Registrar um novo pedido realizado por um cliente, vinculado ao responsável (usuário).\n"
        "- Permite rastrear quem criou o pedido."
    ),
)
def create_new_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = create_order(db, order_in, current_user.id)
    return order


@router.get(
    "/",
    response_model=List[OrderOut],
    summary="Listar pedidos",
    description=(
        "Lista todos os pedidos do sistema, dependendo do tipo de usuário.\n\n"
        "Regras de negócio:\n"
        "- Usuários admin visualizam todos os pedidos.\n"
        "- Usuários comuns visualizam apenas os pedidos que criaram.\n\n"
        "Casos de uso:\n"
        "- Consulta geral de pedidos para administração.\n"
        "- Visualização de histórico de pedidos por usuário."
    ),
)
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = getattr(current_user, "is_admin", False)
    orders = list_orders(db, current_user.id, is_admin)
    return orders


@router.get(
    "/{order_id}",
    response_model=OrderOut,
    summary="Obter pedido por ID",
    description=(
        "Busca um pedido específico pelo seu ID.\n\n"
        "Regras de negócio:\n"
        "- Usuários admin podem acessar qualquer pedido.\n"
        "- Usuários comuns só podem acessar pedidos que eles mesmos criaram.\n"
        "- Retorna erro 404 se o pedido não for encontrado ou se o acesso for negado.\n\n"
        "Casos de uso:\n"
        "- Verificar detalhes de um pedido específico.\n"
        "- Permite auditoria ou acompanhamento de pedidos individuais."
    ),
)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = getattr(current_user, "is_admin", False)
    order = get_order(db, order_id, current_user.id, is_admin)
    return order


@router.put(
    "/{order_id}",
    response_model=OrderOut,
    summary="Atualizar pedido",
    description=(
        "Atualiza os dados de um pedido existente.\n\n"
        "Regras de negócio:\n"
        "- Usuários admin podem atualizar qualquer pedido.\n"
        "- Usuários comuns só podem atualizar pedidos criados por eles.\n"
        "- Retorna erro 404 se o pedido não for encontrado ou se o acesso for negado.\n\n"
        "Casos de uso:\n"
        "- Corrigir informações de um pedido.\n"
        "- Atualizar quantidade ou itens de um pedido antes do processamento."
    ),
)
def update_order_by_id(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = getattr(current_user, "is_admin", False)
    order = update_order(db, order_id, order_update, current_user.id, is_admin)
    return order


@router.delete(
    "/{order_id}",
    summary="Deletar pedido",
    description=(
        "Remove um pedido do sistema.\n\n"
        "Regras de negócio:\n"
        "- Usuários admin podem deletar qualquer pedido.\n"
        "- Usuários comuns só podem deletar pedidos criados por eles.\n"
        "- Retorna erro 404 se o pedido não for encontrado ou se o acesso for negado.\n\n"
        "Casos de uso:\n"
        "- Cancelamento de pedidos indevidos ou duplicados.\n"
        "- Remoção de pedidos antigos não processados."
    ),
)
def delete_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = getattr(current_user, "is_admin", False)
    return delete_order(db, order_id, current_user.id, is_admin)
