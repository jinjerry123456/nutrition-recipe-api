import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import get_db
from app.main import app
from app.models import Base, Category, MenuItem


SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def set_test_auth_env() -> Generator[None, None, None]:
    os.environ["DEMO_USERNAME"] = "student"
    os.environ["DEMO_PASSWORD"] = "coursework123"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    yield


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    category = Category(name="Burgers")
    db.add(category)
    db.flush()
    db.add_all(
        [
            MenuItem(
                category_id=category.id,
                name="Chicken Burger",
                serve_size="1 pc",
                energy_kcal=420,
                protein_g=23,
                total_fat_g=18,
                total_carbs_g=35,
            ),
            MenuItem(
                category_id=category.id,
                name="Veggie Wrap",
                serve_size="1 wrap",
                energy_kcal=320,
                protein_g=14,
                total_fat_g=12,
                total_carbs_g=40,
            ),
        ]
    )
    db.commit()
    yield db
    db.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
