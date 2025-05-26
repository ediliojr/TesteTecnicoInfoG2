import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.utils.file_utils import delete_image, save_base64_image
from app.validations.product_validation import (
    validate_unique_barcode,
    validate_expiration_date,
)

IMAGE_FOLDER = "app/static/images"


def create_product(db: Session, product: ProductCreate) -> Product:
    # Validações
    validate_unique_barcode(db, product.barcode)
    validate_expiration_date(product.expiration_date)

    image_path = save_base64_image(product.image_base64)

    db_product = Product(
        description=product.description,
        price=product.price,
        barcode=product.barcode,
        section=product.section,
        stock=product.stock,
        expiration_date=product.expiration_date,
        image_path=image_path,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, updates: ProductUpdate) -> Product:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise ValueError("Produto não encontrado")

    updates_dict = updates.model_dump(exclude_unset=True)

    # Validações
    validate_unique_barcode(db, updates_dict.get("barcode"), product_id=db_product.id)
    validate_expiration_date(updates_dict.get("expiration_date"))

    for field, value in updates_dict.items():
        if field == "image_base64" and value:
            db_product.image_path = save_base64_image(value)
        elif field != "image_base64":
            setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    section: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available: Optional[bool] = None,
) -> List[Product]:
    query = db.query(Product)

    if section:
        query = query.filter(Product.section == section)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if available is True:
        query = query.filter(Product.stock > 0)
    elif available is False:
        query = query.filter(Product.stock <= 0)

    return query.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.get(Product, product_id)


def delete_product(db: Session, product_id: int) -> bool:
    product = db.get(Product, product_id)
    if not product:
        return False

    # Deleta a imagem se existir
    delete_image(product.image_path)

    db.delete(product)
    db.commit()
    return True
