from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    cuisine: str = Field(min_length=2, max_length=80)
    ingredients: str = Field(min_length=5, description="Comma-separated ingredients")
    calories: float = Field(gt=0, le=3000)
    protein_g: float = Field(ge=0, le=500)
    carbs_g: float = Field(ge=0, le=500)
    fat_g: float = Field(ge=0, le=300)


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    cuisine: str | None = Field(default=None, min_length=2, max_length=80)
    ingredients: str | None = Field(default=None, min_length=5)
    calories: float | None = Field(default=None, gt=0, le=3000)
    protein_g: float | None = Field(default=None, ge=0, le=500)
    carbs_g: float | None = Field(default=None, ge=0, le=500)
    fat_g: float | None = Field(default=None, ge=0, le=300)


class RecipeRead(RecipeBase):
    id: int

    class Config:
        from_attributes = True


class NutritionSummary(BaseModel):
    total_recipes: int
    avg_calories: float
    avg_protein_g: float
    avg_carbs_g: float
    avg_fat_g: float
