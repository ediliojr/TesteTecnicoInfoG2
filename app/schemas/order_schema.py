from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from app.schemas.product_schema import ProductOut


class OrderProductBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderProductCreate(OrderProductBase):
    pass


class OrderProductUpdate(OrderProductBase):
    id: int


class OrderProductOut(OrderProductBase):
    id: int
    product: ProductOut

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    client_id: int
    status: Optional[str] = "pending"


class OrderCreate(OrderBase):
    products: List[OrderProductCreate]


class OrderUpdate(BaseModel):
    client_id: Optional[int] = None
    status: Optional[str] = None
    products: Optional[List[OrderProductUpdate]] = None


class OrderOut(OrderBase):
    id: int
    created_by: int
    products: List[OrderProductOut]

    model_config = ConfigDict(from_attributes=True)
