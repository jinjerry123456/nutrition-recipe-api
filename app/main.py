# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import engine, get_db

app = FastAPI(
    title="McDonald's Nutrition API",
    description="印度麦当劳营养成分分析 API。支持查询、分类与营养计算。",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "欢迎来到麦当劳营养 API！请访问 http://127.0.0.1:8000/docs 查看 API 文档。"}

# 接口 1: 获取所有分类
@app.get("/categories", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

# 接口 2: 分页获取所有菜品
@app.get("/items", response_model=List[schemas.MenuItemResponse], tags=["Menu Items"])
def get_items(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    items = db.query(models.MenuItem).offset(skip).limit(limit).all()
    return items

# 接口 3: 获取特定分类下的所有菜品 (展示了关系型数据库的优势)
@app.get("/categories/{category_id}/items", response_model=List[schemas.MenuItemResponse], tags=["Categories"])
def get_items_by_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="未找到该分类")
    # 直接通过模型关联获取该分类下的所有菜品
    return category.items