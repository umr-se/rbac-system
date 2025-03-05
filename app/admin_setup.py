from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.crud as crud
from app.schemas import UserCreate
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from models import User

# Rest of your admin setup code

# Initialize database session
db: Session = SessionLocal()

# Admin credentials
admin_data = UserCreate(
    name="Admin User",
    email="admin@example.com",
    password="pass123"
)

# Check if admin already exists before creating a new one
existing_admin = crud.get_user(db, admin_data.email)
if not existing_admin:
    admin_user = crud.create_user(db, admin_data, is_admin=True)
    db.commit()  # Commit the transaction
    print(f"Admin user created: {admin_user.email}")
else:
    print("Admin user already exists.")

# Close session
db.close()
