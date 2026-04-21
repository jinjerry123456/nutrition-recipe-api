# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Keep one source of truth for DB connectivity so local and hosted runs use the same code path.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mcdonalds_nutrition.db")
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    # Normalize legacy provider URLs to SQLAlchemy-compatible format.
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs thread-safety flags in dev mode; other engines do not.
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    # Centralized session lifecycle keeps request handlers focused on business logic.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()