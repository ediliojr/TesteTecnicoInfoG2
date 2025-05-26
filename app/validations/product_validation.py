from fastapi import HTTPException
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models.product_model import Product


def validate_unique_barcode(
    db: Session, barcode: Optional[str], product_id: int = None
):
    if not barcode:
        return
    query = db.query(Product).filter(Product.barcode == barcode)
    if product_id is not None:
        query = query.filter(Product.id != product_id)
    if query.first():
        raise HTTPException(
            status_code=400, detail="Barcode already exists for another product"
        )


def validate_expiration_date(expiration_date: Optional[date]):
    if not expiration_date:
        return
    if expiration_date < date.today():
        raise HTTPException(
            status_code=400, detail="Validity data cannot be in the past"
        )
