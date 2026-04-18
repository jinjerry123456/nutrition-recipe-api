# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# 获取环境变量中的数据库 URL，如果没有则默认使用本地 SQLite
# Render 提供的 Postgres URL 通常以 postgres:// 开头，但在 SQLAlchemy 中需要换成 postgresql://
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mcdonalds_nutrition.db")
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 如果是本地 SQLite，需要特定的 connect_args，否则留空
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()