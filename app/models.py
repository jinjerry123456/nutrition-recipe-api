# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# Category is the parent dimension for menu browsing and aggregation.
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Example values: Regular Menu, Breakfast.

    # One category -> many menu items, enabling category-level analytics.
    items = relationship("MenuItem", back_populates="category")

# MenuItem is the factual nutrition entity used by search and combo scoring.
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))  # Referential integrity to Category.
    name = Column(String, index=True)
    serve_size = Column(String)

    # Nutrition fields are intentionally atomic so we can extend analytics safely later.
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

    # Relationship hooks for read joins and combo calculations.
    category = relationship("Category", back_populates="items")
    combo_links = relationship("ComboItem", back_populates="menu_item")

# Combo captures user-designed bundles, which is the core CRUD resource.
class Combo(Base):
    __tablename__ = "combos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Example values: Cheat Day Combo, Lean Protein Set.
    description = Column(String, nullable=True)

    # One combo -> many bridge rows for multi-item composition.
    items = relationship("ComboItem", back_populates="combo")

# ComboItem is the bridge table that turns MenuItem into a many-to-many combo system.
class ComboItem(Base):
    __tablename__ = "combo_items"

    id = Column(Integer, primary_key=True, index=True)
    combo_id = Column(Integer, ForeignKey("combos.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)  # Quantity drives nutrition totals and ranking math.

    combo = relationship("Combo", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="combo_links")