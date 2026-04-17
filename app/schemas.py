# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

# --- 菜品 (MenuItem) 的序列化格式 ---
class MenuItemBase(BaseModel):
    name: str
    serve_size: str
    energy_kcal: float
    protein_g: float
    total_fat_g: float
    total_carbs_g: float

class MenuItemResponse(MenuItemBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True  # 允许直接读取数据库模型

# --- 分类 (Category) 的序列化格式 ---
class CategoryBase(BaseModel):
    name: str

class CategoryResponse(CategoryBase):
    id: int
    # 返回分类时，可选择性地不嵌套所有菜品，或者嵌套（这里我们选择简单的）

    class Config:
        from_attributes = True