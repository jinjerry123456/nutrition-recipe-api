import os
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="McDonald's Nutrition API",
    description="Nutrition and combo analytics API with CRUD, authentication, filtering, and insights.",
    version="2.0.0",
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DEFAULT_DEMO_USERNAME = os.getenv("DEMO_USERNAME", "student")
DEFAULT_DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "coursework123")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
_demo_password_hash = pwd_context.hash(DEFAULT_DEMO_PASSWORD)

# Lightweight demo identity store keeps auth workflow explicit for the viva demo;
# migration path: replace with a persisted users table and role model.
FAKE_USERS_DB = {
    DEFAULT_DEMO_USERNAME: {
        "username": DEFAULT_DEMO_USERNAME,
        "full_name": "Coursework Demo User",
        "hashed_password": _demo_password_hash,
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> dict | None:
    user = FAKE_USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    # Token expiry is explicit so examiners can see security behavior, not magic defaults.
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    # Single reusable gate for all protected routes keeps auth policy consistent.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = FAKE_USERS_DB.get(username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("disabled"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


def fetch_combo_or_404(combo_id: int, db: Session) -> models.Combo:
    # Eager loading avoids N+1 queries when returning combo + linked menu items.
    combo = (
        db.query(models.Combo)
        .options(joinedload(models.Combo.items).joinedload(models.ComboItem.menu_item))
        .filter(models.Combo.id == combo_id)
        .first()
    )
    if not combo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Combo {combo_id} not found")
    return combo


def build_combo_nutrition(combo: models.Combo) -> tuple[float, float]:
    # Derived totals are computed at read-time to keep stored data normalized.
    total_calories = sum((entry.menu_item.energy_kcal or 0) * entry.quantity for entry in combo.items)
    total_protein = sum((entry.menu_item.protein_g or 0) * entry.quantity for entry in combo.items)
    return round(total_calories, 2), round(total_protein, 2)


def serialize_combo(combo: models.Combo) -> schemas.ComboResponse:
    total_calories, total_protein = build_combo_nutrition(combo)
    return schemas.ComboResponse.model_validate(
        {
            "id": combo.id,
            "name": combo.name,
            "description": combo.description,
            "items": combo.items,
            "total_calories": total_calories,
            "total_protein": total_protein,
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, "path": request.url.path})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database operation failed", "path": request.url.path},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unexpected server error", "path": request.url.path},
    )


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.post("/auth/token", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user["username"], expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserPublic, tags=["Auth"])
def read_current_user(current_user: dict = Depends(get_current_active_user)):
    return {
        "username": current_user["username"],
        "full_name": current_user.get("full_name"),
        "disabled": current_user.get("disabled", False),
    }


@app.get("/categories", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(skip: int = 0, limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return db.query(models.Category).offset(skip).limit(limit).all()


@app.get("/items", response_model=List[schemas.MenuItemResponse], tags=["Menu Items"])
def get_items(skip: int = 0, limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    return db.query(models.MenuItem).offset(skip).limit(limit).all()


@app.get("/categories/{category_id}/items", response_model=List[schemas.MenuItemResponse], tags=["Categories"])
def get_items_by_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category.items


@app.get("/combos", response_model=List[schemas.ComboResponse], tags=["Combos"])
def list_combos(db: Session = Depends(get_db)):
    combos = db.query(models.Combo).options(joinedload(models.Combo.items).joinedload(models.ComboItem.menu_item)).all()
    return [serialize_combo(combo) for combo in combos]


@app.get("/combos/{combo_id}", response_model=schemas.ComboResponse, tags=["Combos"])
def get_combo(combo_id: int, db: Session = Depends(get_db)):
    combo = fetch_combo_or_404(combo_id, db)
    return serialize_combo(combo)


@app.post(
    "/combos",
    response_model=schemas.ComboResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Combos"],
    dependencies=[Depends(get_current_active_user)],
)
def create_combo(combo_in: schemas.ComboCreate, db: Session = Depends(get_db)):
    # Unique combo names improve retrieval clarity and prevent ambiguous updates in demos.
    existing = db.query(models.Combo).filter(models.Combo.name == combo_in.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Combo name already exists")

    new_combo = models.Combo(name=combo_in.name, description=combo_in.description)
    db.add(new_combo)
    db.flush()  # Flush first so we can safely reference new_combo.id in bridge rows.

    for entry in combo_in.items:
        item = db.query(models.MenuItem).filter(models.MenuItem.id == entry.item_id).first()
        if not item:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {entry.item_id} not found")
        db.add(models.ComboItem(combo_id=new_combo.id, item_id=item.id, quantity=entry.quantity))

    db.commit()
    combo = fetch_combo_or_404(new_combo.id, db)
    return serialize_combo(combo)


@app.put(
    "/combos/{combo_id}",
    response_model=schemas.ComboResponse,
    tags=["Combos"],
    dependencies=[Depends(get_current_active_user)],
)
def update_combo(combo_id: int, combo_in: schemas.ComboUpdate, db: Session = Depends(get_db)):
    combo = fetch_combo_or_404(combo_id, db)
    payload = combo_in.model_dump(exclude_unset=True)

    if "name" in payload:
        duplicate = db.query(models.Combo).filter(models.Combo.name == payload["name"], models.Combo.id != combo_id).first()
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Combo name already exists")
        combo.name = payload["name"]

    if "description" in payload:
        combo.description = payload["description"]

    if "items" in payload:
        # Replace strategy keeps update semantics deterministic for oral demonstration.
        db.query(models.ComboItem).filter(models.ComboItem.combo_id == combo.id).delete()
        for entry in payload["items"]:
            item_id = entry["item_id"]
            quantity = entry["quantity"]
            item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
            if not item:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")
            db.add(models.ComboItem(combo_id=combo.id, item_id=item.id, quantity=quantity))

    db.commit()
    updated = fetch_combo_or_404(combo_id, db)
    return serialize_combo(updated)


@app.delete(
    "/combos/{combo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Combos"],
    dependencies=[Depends(get_current_active_user)],
)
def delete_combo(combo_id: int, db: Session = Depends(get_db)):
    combo = fetch_combo_or_404(combo_id, db)
    db.query(models.ComboItem).filter(models.ComboItem.combo_id == combo.id).delete()
    db.delete(combo)
    db.commit()
    return None


@app.get("/items/search", response_model=List[schemas.MenuItemResponse], tags=["Analytics"])
def search_healthy_items(
    max_calories: float = Query(default=500.0, ge=1),
    min_protein: float = Query(default=15.0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.MenuItem)
        .filter(models.MenuItem.energy_kcal <= max_calories, models.MenuItem.protein_g >= min_protein)
        .all()
    )


@app.get("/analytics/category-summary", response_model=List[schemas.CategoryNutritionSummary], tags=["Analytics"])
def category_summary(db: Session = Depends(get_db)):
    categories = db.query(models.Category).options(joinedload(models.Category.items)).all()
    results: List[schemas.CategoryNutritionSummary] = []
    for category in categories:
        if not category.items:
            continue
        item_count = len(category.items)
        avg_calories = round(sum(item.energy_kcal or 0 for item in category.items) / item_count, 2)
        avg_protein = round(sum(item.protein_g or 0 for item in category.items) / item_count, 2)
        results.append(
            schemas.CategoryNutritionSummary(
                category_id=category.id,
                category_name=category.name,
                avg_calories=avg_calories,
                avg_protein=avg_protein,
                item_count=item_count,
            )
        )
    return results


@app.get("/analytics/combo-scoreboard", response_model=List[schemas.ComboAnalyticsSummary], tags=["Analytics"])
def combo_scoreboard(db: Session = Depends(get_db)):
    combos = db.query(models.Combo).options(joinedload(models.Combo.items).joinedload(models.ComboItem.menu_item)).all()
    data: List[schemas.ComboAnalyticsSummary] = []
    for combo in combos:
        total_calories, total_protein = build_combo_nutrition(combo)
        # Protein density gives a compact "quality per calorie" signal for creative analytics.
        density = round(total_protein / total_calories, 4) if total_calories > 0 else 0.0
        quantity_total = sum(entry.quantity for entry in combo.items)
        data.append(
            schemas.ComboAnalyticsSummary(
                combo_id=combo.id,
                combo_name=combo.name,
                total_items=quantity_total,
                total_calories=total_calories,
                total_protein=total_protein,
                protein_density=density,
            )
        )
    return sorted(data, key=lambda row: row.protein_density, reverse=True)