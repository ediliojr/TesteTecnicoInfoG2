from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.db.database import get_db
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import (
    get_products as service_get_products,
    get_product_by_id,
    create_product as service_create_product,
    update_product as service_update_product,
    delete_product as service_delete_product,
)
from app.routes.auth_route import get_current_user, require_admin

IMAGE_FOLDER = "app/static/images"

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "/",
    response_model=List[ProductOut],
    summary="Listar produtos",
    description=(
        "Retorna uma lista de produtos com filtros opcionais.\n\n"
        "Regras de negócio:\n"
        "- Pode ser usado por qualquer usuário autenticado.\n"
        "- Filtros disponíveis: seção (`section`), preço mínimo e máximo (`min_price`, `max_price`), disponibilidade (`available`).\n"
        "- Paginação controlada pelos parâmetros `skip` e `limit`.\n\n"
        "Casos de uso:\n"
        "- Navegar por todos os produtos.\n"
        "- Buscar produtos dentro de uma faixa de preço específica.\n"
        "- Listar apenas produtos disponíveis para venda."
    ),
)
def get_products(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    section: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    available: Optional[bool] = Query(None),
):
    return service_get_products(
        db, skip, limit, section, min_price, max_price, available
    )


@router.post(
    "/",
    response_model=ProductOut,
    summary="Criar produto",
    description=(
        "Cria um novo produto no sistema.\n\n"
        "Regras de negócio:\n"
        "- Somente usuários com permissão de administrador podem acessar esta rota.\n"
        "- O produto deve conter nome, descrição, preço, seção e disponibilidade.\n\n"
        "Casos de uso:\n"
        "- Adicionar novos produtos ao catálogo.\n"
        "- Atualizar o estoque com novos itens disponíveis."
    ),
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return service_create_product(db, product)


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Obter produto por ID",
    description=(
        "Retorna os detalhes de um produto específico.\n\n"
        "Regras de negócio:\n"
        "- Qualquer usuário autenticado pode acessar.\n"
        "- Retorna erro 404 caso o produto não seja encontrado.\n\n"
        "Casos de uso:\n"
        "- Visualizar as informações completas de um produto antes de comprar.\n"
        "- Verificar disponibilidade, descrição e preço de um produto."
    ),
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    summary="Atualizar produto",
    description=(
        "Atualiza os dados de um produto existente.\n\n"
        "Regras de negócio:\n"
        "- Apenas administradores podem acessar esta rota.\n"
        "- Retorna erro 404 se o produto não existir.\n\n"
        "Casos de uso:\n"
        "- Corrigir informações incorretas sobre um produto.\n"
        "- Atualizar preço ou disponibilidade de um item do catálogo."
    ),
)
def update_product(
    product_id: int,
    update_data: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    product = service_update_product(db, product_id, update_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete(
    "/{product_id}",
    summary="Deletar produto",
    description=(
        "Remove um produto do sistema.\n\n"
        "Regras de negócio:\n"
        "- Apenas administradores podem acessar esta rota.\n"
        "- Retorna erro 404 se o produto não existir.\n\n"
        "Casos de uso:\n"
        "- Remover produtos descontinuados do catálogo.\n"
        "- Apagar itens com erro de cadastro."
    ),
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    success = service_delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted successfully"}


@router.get(
    "/images/{image_filename}",
    summary="Servir imagem do produto",
    description=(
        "Serve imagens estáticas dos produtos com base no nome do arquivo.\n\n"
        "Regras de negócio:\n"
        "- Qualquer usuário pode acessar esta rota.\n"
        "- A imagem deve estar salva na pasta `app/static/images`.\n"
        "- Retorna erro 404 se a imagem não existir.\n\n"
        "Casos de uso:\n"
        "- Carregar imagens dos produtos para exibição no frontend."
    ),
)
def serve_product_image(image_filename: str):
    file_path = os.path.join(IMAGE_FOLDER, image_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)
