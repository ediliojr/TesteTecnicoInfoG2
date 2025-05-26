# schemas/product_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class ProductBase(BaseModel):
    description: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    barcode: str = Field(..., min_length=1)
    section: str = Field(..., min_length=1)
    stock: int = Field(..., ge=0)
    expiration_date: Optional[date] = None


class ProductCreate(ProductBase):
    image_base64: str = Field(..., description="Imagem em base64")


class ProductUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, ge=0)
    barcode: Optional[str] = Field(None, min_length=1)
    section: Optional[str] = Field(None, min_length=1)
    stock: Optional[int] = Field(None, ge=0)
    expiration_date: Optional[date] = None
    image_base64: Optional[str] = Field(
        None, description="Imagem nova em base64 (opcional)"
    )


class ProductOut(ProductBase):
    id: int
    image_path: str

    model_config = ConfigDict(from_attributes=True)
