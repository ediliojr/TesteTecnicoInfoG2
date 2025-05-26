from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes import auth_route, order_route, client_route, product_route
from app.utils.sentry import init_sentry

init_sentry()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_route.router)
app.include_router(client_route.router)
app.include_router(product_route.router)
app.include_router(order_route.router)