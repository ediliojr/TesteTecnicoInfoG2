from fastapi import HTTPException, status


def validate_email_not_registered(db, email: str):
    from app.models.user_model import User

    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already in use",
        )
