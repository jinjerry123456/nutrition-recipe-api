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

# app/main.py 续写

# 接口 4: 创建自定义套餐并自动计算营养
@app.post("/combos", response_model=schemas.ComboResponse, tags=["Combos"])
def create_combo(combo_in: schemas.ComboCreate, db: Session = Depends(get_db)):
    # 1. 创建套餐基本信息
    new_combo = models.Combo(name=combo_in.name, description=combo_in.description)
    db.add(new_combo)
    db.flush() # 获取生成的 combo ID

    total_cal = 0
    total_pro = 0

    # 2. 处理套餐内的每一个单品
    for entry in combo_in.items:
        item = db.query(models.MenuItem).filter(models.MenuItem.id == entry.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {entry.item_id} not found")
        
        # 建立中间表关联
        db_combo_item = models.ComboItem(
            combo_id=new_combo.id,
            item_id=item.id,
            quantity=entry.quantity
        )
        db.add(db_combo_item)
        
        # 累加营养数据（核心逻辑）
        total_cal += item.energy_kcal * entry.quantity
        total_pro += item.protein_g * entry.quantity

    db.commit()
    db.refresh(new_combo)
    
    # 动态注入计算结果
    new_combo.total_calories = round(total_cal, 2)
    new_combo.total_protein = round(total_pro, 2)
    
    return new_combo

# 接口 5: 高级筛选 - 寻找健身餐（例如：高蛋白且卡路里低于某值的单品）
@app.get("/items/search", response_model=List[schemas.MenuItemResponse], tags=["Analytics"])
def search_healthy_items(
    max_calories: float = 500.0, 
    min_protein: float = 15.0, 
    db: Session = Depends(get_db)
):
    items = db.query(models.MenuItem).filter(
        models.MenuItem.energy_kcal <= max_calories,
        models.MenuItem.protein_g >= min_protein
    ).all()
    return items