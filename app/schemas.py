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
        from_attributes = True

# --- 分类 (Category) 的序列化格式 ---
class CategoryBase(BaseModel):
    name: str

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- 套餐条目 (ComboItem) ---
class ComboItemCreate(BaseModel):
    item_id: int
    quantity: int = 1

class ComboItemResponse(BaseModel):
    menu_item: MenuItemResponse
    quantity: int

    class Config:
        from_attributes = True

# --- 套餐 (Combo) ---
class ComboBase(BaseModel):
    name: str
    description: Optional[str] = None

class ComboCreate(ComboBase):
    items: List[ComboItemCreate] # 创建时传入菜品 ID 列表

class ComboResponse(ComboBase):
    id: int
    items: List[ComboItemResponse]
    
    # 满分亮点：自动计算总营养
    total_calories: float = 0.0
    total_protein: float = 0.0

    class Config:
        from_attributes = True