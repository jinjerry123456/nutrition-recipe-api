# app/schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    serve_size: str = Field(..., min_length=1, max_length=100)
    energy_kcal: float = Field(..., ge=0)
    protein_g: float = Field(..., ge=0)
    total_fat_g: float = Field(..., ge=0)
    total_carbs_g: float = Field(..., ge=0)


class MenuItemResponse(MenuItemBase):
    id: int
    category_id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str


class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ComboItemCreate(BaseModel):
    item_id: int
    quantity: int = Field(default=1, ge=1)

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("quantity must be at least 1")
        return v


class ComboItemResponse(BaseModel):
    menu_item: MenuItemResponse
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class ComboBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ComboCreate(ComboBase):
    items: List[ComboItemCreate] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def non_empty_items(cls, v: List[ComboItemCreate]) -> List[ComboItemCreate]:
        if not v:
            raise ValueError("套餐至少包含一道菜品")
        return v


class ComboUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    items: Optional[List[ComboItemCreate]] = None


class ComboResponse(ComboBase):
    id: int
    items: List[ComboItemResponse]
    total_calories: float = 0.0
    total_protein: float = 0.0
    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    detail: str | List[dict]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str
    exp: int


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserPublic(BaseModel):
    username: str
    full_name: Optional[str] = None
    disabled: bool = False


class ComboAnalyticsSummary(BaseModel):
    combo_id: int
    combo_name: str
    total_items: int
    total_calories: float
    total_protein: float
    protein_density: float


class CategoryNutritionSummary(BaseModel):
    category_id: int
    category_name: str
    avg_calories: float
    avg_protein: float
    item_count: int
