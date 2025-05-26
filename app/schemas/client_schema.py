from pydantic import BaseModel, EmailStr, ConfigDict, constr
from typing import Optional

# Define o tipo CPF com restrições de tamanho (11 dígitos)
CPFStr = constr(min_length=11, max_length=11)


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: CPFStr  # type: ignore
    whatsapp: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[CPFStr] = None  # type: ignore
    whatsapp: Optional[str] = None


class ClientOut(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
