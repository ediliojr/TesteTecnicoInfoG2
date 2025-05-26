from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth_schema import UserCreate, UserOut, Token
from app.models.user_model import User
from app.db.database import get_db
from app.services.auth_service import (
    authenticate_user,
    create_user,
    generate_tokens,
    refresh_tokens,
    get_current_user,
    require_admin,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    summary="Registro de novo usuário",
    description=(
        "Registra um novo usuário com email e senha.\n\n"
        "Regras de negócio:\n"
        "- O email deve ser único no sistema.\n"
        "- A senha deve atender requisitos mínimos de segurança (validação no serviço).\n\n"
        "Casos de uso:\n"
        "- Novo usuário pode se cadastrar para acessar o sistema."
    ),
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(db, user.email, user.password)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Autenticação de usuário",
    description=(
        "Autentica o usuário usando email e senha.\n\n"
        "Regras de negócio:\n"
        "- Valida as credenciais do usuário.\n"
        "- Emite tokens JWT de acesso e refresh para uso em autenticação contínua.\n\n"
        "Casos de uso:\n"
        "- Usuário realiza login para obter tokens e acessar recursos protegidos."
    ),
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, refresh_token = generate_tokens(user.email)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.delete(
    "/delete",
    status_code=204,
    summary="Excluir usuário autenticado",
    description=(
        "Exclui o usuário atualmente autenticado do sistema.\n\n"
        "Regras de negócio:\n"
        "- Apenas o próprio usuário pode excluir sua conta.\n"
        "- A exclusão é definitiva.\n\n"
        "Casos de uso:\n"
        "- Usuário deseja remover sua conta permanentemente."
    ),
)
def delete_current_user(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    return None


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh de token JWT",
    description=(
        "Renova tokens JWT usando um refresh token válido.\n\n"
        "Regras de negócio:\n"
        "- O refresh token deve ser válido e não expirado.\n"
        "- Emite novos tokens de acesso e refresh.\n\n"
        "Casos de uso:\n"
        "- Usuário mantém sessão ativa sem precisar fazer login novamente."
    ),
)
def refresh_token(refresh_token: str = Body(...)):
    access_token, new_refresh_token = refresh_tokens(refresh_token)
    if not access_token or not new_refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
