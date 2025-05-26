from app.models.client_model import Client
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.order_model import Order, OrderProduct
from app.schemas.order_schema import OrderCreate, OrderUpdate
from app.models.product_model import Product
from app.utils.send_sms import send_whatsapp_message
from app.validations.order_validation import adjust_stock, validate_stock


def get_order(db: Session, order_id: int, user_id: int, is_admin: bool):
    # Busca pedido pelo ID
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Permite acesso somente se for admin ou dono do pedido
    if not is_admin and order.created_by != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return order


def list_orders(db: Session, user_id: int, is_admin: bool):
    # Lista todos pedidos para admin, ou só os do usuário comum
    if is_admin:
        return db.query(Order).all()
    else:
        return db.query(Order).filter(Order.created_by == user_id).all()


def create_order(db: Session, order_in: OrderCreate, user_id: int):
    # Valida se há estoque suficiente para todos os produtos
    validate_stock(db, order_in.products)

    # Cria pedido e adiciona ao DB
    db_order = Order(
        client_id=order_in.client_id, status=order_in.status, created_by=user_id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Adiciona produtos ao pedido e atualiza estoque
    for item in order_in.products:
        order_product = OrderProduct(
            order_id=db_order.id, product_id=item.product_id, quantity=item.quantity
        )
        db.add(order_product)
        adjust_stock(db, item.product_id, -item.quantity)

    db.commit()
    db.refresh(db_order)

    # Busca o cliente para pegar o telefone do WhatsApp
    client = db.query(Client).filter(Client.id == order_in.client_id).first()
    if client and client.whatsapp:
        message = f"Olá {client.name}, seu pedido #{db_order.id} foi criado com sucesso! Obrigado pela preferência."
        send_whatsapp_message(client.whatsapp, message)

    return db_order


def update_order(
    db: Session, order_id: int, order_update: OrderUpdate, user_id: int, is_admin: bool
):
    # Busca pedido para atualização
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Atualiza campos básicos do pedido
    if order_update.status is not None:
        order.status = order_update.status
    if order_update.client_id is not None:
        order.client_id = order_update.client_id

    current_products = {p.id: p for p in order.products}
    updated_products = order_update.products or []

    updated_ids = {p.id for p in updated_products if p.id is not None}
    current_ids = set(current_products.keys())

    # Identifica produtos removidos
    removed_products = [current_products[p_id] for p_id in current_ids - updated_ids]

    # Prepara lista de produtos para validar e ajustar estoque
    product_ids = set()
    product_ids.update([p.product_id for p in removed_products])
    product_ids.update([p.product_id for p in updated_products])
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    # Repõe estoque dos produtos removidos
    for removed in removed_products:
        adjust_stock(db, removed.product_id, removed.quantity)
        db.delete(removed)

    # Atualiza quantidades ou adiciona novos produtos no pedido
    for p_data in updated_products:
        if p_data.id in current_products:
            order_prod = current_products[p_data.id]
            product = product_map.get(order_prod.product_id)

            diff = p_data.quantity - order_prod.quantity

            # Checa estoque se aumentando quantidade
            if diff > 0 and product.stock < diff:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.description}",
                )

            adjust_stock(db, order_prod.product_id, -diff)
            order_prod.quantity = p_data.quantity
            db.add(order_prod)
        else:
            product = product_map.get(p_data.product_id)
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product {p_data.product_id} not found"
                )
            if product.stock < p_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.description}",
                )

            new_order_product = OrderProduct(
                order_id=order.id,
                product_id=p_data.product_id,
                quantity=p_data.quantity,
            )
            db.add(new_order_product)
            adjust_stock(db, p_data.product_id, -p_data.quantity)

    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int, user_id: int, is_admin: bool):
    # Busca pedido para deletar
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Só admin ou dono podem deletar
    if not is_admin and order.created_by != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Repõe estoque antes de deletar o pedido
    for order_product in order.products:
        adjust_stock(db, order_product.product_id, order_product.quantity)

    db.delete(order)
    db.commit()

    return {"detail": "Order deleted successfully"}
