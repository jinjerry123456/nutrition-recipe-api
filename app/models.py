# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# 1. 分类表 (Category) - 一对多关联
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # 例如：Regular Menu, Breakfast 等

    # 建立与菜品的关联
    items = relationship("MenuItem", back_populates="category")

# 2. 菜品核心表 (MenuItem)
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id")) # 外键关联分类
    name = Column(String, index=True)
    serve_size = Column(String)
    
    # 营养成分数据
    energy_kcal = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    total_fat_g = Column(Float, default=0.0)
    sat_fat_g = Column(Float, default=0.0)
    trans_fat_g = Column(Float, default=0.0)
    cholesterol_mg = Column(Float, default=0.0)
    total_carbs_g = Column(Float, default=0.0)
    total_sugars_g = Column(Float, default=0.0)
    added_sugars_g = Column(Float, default=0.0)
    sodium_mg = Column(Float, default=0.0)

    # 关联关系
    category = relationship("Category", back_populates="items")
    combo_links = relationship("ComboItem", back_populates="menu_item")

# 3. 套餐表 (Combo) - 满分亮点：让用户自己搭配套餐
class Combo(Base):
    __tablename__ = "combos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # 例如："我的欺骗餐", "高蛋白增肌套餐"
    description = Column(String, nullable=True)

    items = relationship("ComboItem", back_populates="combo")

# 4. 套餐-菜品关联表 (多对多中间表)
class ComboItem(Base):
    __tablename__ = "combo_items"

    id = Column(Integer, primary_key=True, index=True)
    combo_id = Column(Integer, ForeignKey("combos.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1) # 点了几个

    combo = relationship("Combo", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="combo_links")