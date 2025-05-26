import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.db.database import Base
from app.models.user_model import User
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

def toggle_admin_status(user_identifier: str):
    session = Session(bind=engine)
    user = session.query(User).filter(User.email == user_identifier).first()

    if not user:
        print(f"Usuário '{user_identifier}' não encontrado.")
        return

    user.is_admin = 0 if user.is_admin == 1 else 1
    session.commit()
    status = "admin" if user.is_admin == 1 else "usuário normal"
    print(f"Usuário '{user_identifier}' agora é {status}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python toggle_admin.py <email_do_usuario>")
        sys.exit(1)
    toggle_admin_status(sys.argv[1])
