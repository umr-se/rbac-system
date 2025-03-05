from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate, is_admin: bool = False):
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(
        name=user_data.name, 
        email=user_data.email, 
        password=hashed_password, 
        is_admin=is_admin  # Set admin flag based on input
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session):
    """Retrieve all users."""
    return db.query(User).all()


def delete_user(db: Session, user_id: int):
    """Delete a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


def delete_all_users(db: Session):
    """Delete all users (Only Admins can perform this)."""
    db.query(User).delete()
    db.commit()


def update_user(db: Session, user_id: int, name: str, email: str):
    """Update a user's name and email."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.email = email
        db.commit()
        db.refresh(user)
        return user
    return None
