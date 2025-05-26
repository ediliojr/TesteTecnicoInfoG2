from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.client_model import Client


def validate_unique_email(db: Session, email: str, client_id: int = None):
    query = db.query(Client).filter_by(email=email)
    if client_id is not None:
        query = query.filter(Client.id != client_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Email is already in use")


def validate_unique_cpf(db: Session, cpf: str, client_id: int = None):
    query = db.query(Client).filter_by(cpf=cpf)
    if client_id is not None:
        query = query.filter(Client.id != client_id)
    if query.first():
        raise HTTPException(status_code=400, detail="CPF is already in use")
