# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# 加载环境变量（你需要建一个 .env 文件把数据库密码存起来，别传到 GitHub 上）
load_dotenv()

# 这里暂时用本地的 SQLite 数据库方便你快速测试，之后部署 Render 时只需改这个 URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mcdonalds_nutrition.db")

# 如果使用的是 SQLite，需要添加 check_same_thread=False
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 获取数据库会话的依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()