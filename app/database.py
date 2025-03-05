from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# database.py
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://DATABASE_USER:PASSWORD@mysql-db:3###/YOUR_DATABASE?charset=utf8mb4")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
