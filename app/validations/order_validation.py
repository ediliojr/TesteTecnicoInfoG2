# app/utils/stock_utils.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.product_model import Product
from app.schemas.order_schema import OrderProductBase


def validate_stock(db: Session, items: List[OrderProductBase]):
    product_ids = [item.product_id for item in items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    for item in items:
        product = product_map.get(item.product_id)
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Produto {item.product_id} não encontrado"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para produto {product.description}",
            )


def adjust_stock(db: Session, product_id: int, quantity_change: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Produto {product_id} não encontrado"
        )

    new_stock = product.stock + quantity_change
    if new_stock < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente para produto {product.description}",
        )

    product.stock = new_stock
    db.add(product)
