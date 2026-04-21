# Nutrition & Recipe Analytics API

RESTful API coursework project for `XJCO3011 Web Services and Web Data`, built with FastAPI and SQLAlchemy.

This project demonstrates:
- Full CRUD for a core resource (`Combo`)
- JWT authentication for protected operations
- Validation and robust error handling
- Creative analytics endpoints over nutrition data
- Automated tests for core and edge scenarios

---

## 1) Coursework Deliverables

This repository is structured to support all required submission artifacts:

- Public source code repository with clear commit history
- Setup and usage guide (`README.md`)
- API documentation PDF: [`document/API Documentation.pdf`](document/API%20Documentation.pdf)
- Technical report PDF (max 5 pages): [`document/Technical Report.pdf`](document/Technical%20Report.pdf)
- Presentation slides (PPTX): [`document/slide.pptx`](document/slide.pptx)
- GenAI declaration and exported logs appendix (inside report appendix, or add files under `document/`)

Links required for submission:
- GitHub repository: `https://github.com/jinjerry123456/nutrition-recipe-api`
- Live deployment (Render): `https://mcdonalds-api-jhd9.onrender.com`

---

## 2) Project Scope

### Domain
Nutrition and recipe analytics using the India McDonald's nutrition dataset.

### Core design goals
- Build a data-driven API with SQL-backed persistence
- Keep the architecture easy to justify in oral examination
- Show independent engineering decisions beyond minimum pass requirements

### Technology stack
- **FastAPI**: API framework + automatic OpenAPI docs
- **SQLAlchemy**: relational data modeling and ORM querying
- **SQLite / PostgreSQL**: local and production database compatibility
- **JWT (`python-jose`) + password hashing (`passlib`)**: authenticated write operations
- **Pytest + TestClient**: automated API verification

---

## 3) Quick Start

### 3.1 Prerequisites
- Python 3.10+
- `pip`

### 3.2 Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.3 Environment variables

Create `.env` in project root:

```env
DATABASE_URL=sqlite:///./mcdonalds_nutrition.db
JWT_SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEMO_USERNAME=student
DEMO_PASSWORD=coursework123
```

### 3.4 Run the API

```bash
uvicorn app.main:app --reload
```

Open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 3.5 Seed dataset (optional but recommended)

```bash
python seed.py
```

---

## 4) Authentication Workflow (JWT)

### Step 1: request access token

```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student&password=coursework123"
```

### Step 2: call protected endpoints with Bearer token

```bash
curl -X POST "http://127.0.0.1:8000/combos" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Gym Combo",
    "description":"High-protein lunch set",
    "items":[{"item_id":1,"quantity":2}]
  }'
```

---

## 5) API Surface

### Auth
- `POST /auth/token` - login and obtain JWT
- `GET /auth/me` - inspect current authenticated user

### Browsing and filtering
- `GET /categories`
- `GET /categories/{category_id}/items`
- `GET /items`
- `GET /items/search?max_calories=500&min_protein=15`

### Core CRUD (`Combo`)
- `GET /combos`
- `GET /combos/{combo_id}`
- `POST /combos` (protected)
- `PUT /combos/{combo_id}` (protected)
- `DELETE /combos/{combo_id}` (protected)

### Analytics
- `GET /analytics/category-summary`
- `GET /analytics/combo-scoreboard`

---

## 6) Validation and Error Handling

Implemented controls include:
- Request schema validation (length, range, required fields)
- Business constraints (duplicate combo name conflict, missing item references)
- Auth failures with standards-based status codes
- Resource-not-found handling
- Global exception handlers for database and unexpected runtime failures

Typical status codes used:
- `200`, `201`, `204`
- `401`, `403`, `404`, `409`, `422`, `500`

---

## 7) Testing

Run all tests:

```bash
pytest -q
```

Covered scenarios:
- JWT login success and failure
- Unauthorized access to protected CRUD endpoints
- End-to-end Combo CRUD workflow
- Invalid item references (`404`)
- Validation edge case (`422` for invalid quantity)
- Analytics endpoint correctness and ordering

---

## 8) Repository Structure

```text
nutrition-recipe-api/
  app/
    database.py
    main.py
    models.py
    schemas.py
  dataset/
    India_Menu.csv
  tests/
    conftest.py
    test_api.py
  seed.py
  requirements.txt
  README.md
```

---

## 9) Deployment Notes

- Local development uses SQLite by default.
- Production deployment should use PostgreSQL via `DATABASE_URL`.
- Supported hosting options: Render, Railway, PythonAnywhere, or equivalent.
- Ensure deployed version exactly matches the version demonstrated in oral exam.

---

## 10) Marking Rubric Mapping

### Content (75%)
- **API functionality & implementation**: complete SQL-backed CRUD + analytics routes
- **Code quality & architecture**: relational model design, schema-based validation, reusable auth/error layers
- **Documentation**: executable README + OpenAPI docs + PDF documentation artifact
- **Version control & deployment**: structured commits and deployment-ready config
- **Testing & error handling**: automated tests with core and edge-case checks
- **Creativity & GenAI usage**: nutrition scoring logic + documented AI-supported development workflow

### Presentation (15%)
- Include architecture diagram, ER diagram, endpoint demo flow, test evidence, and deployment evidence.

### Q&A (10%)
- Be ready to justify design trade-offs, JWT flow, status code choices, analytics formulation, and extension plan.

---

## 11) GenAI Declaration Guidance (for report appendix)

In your technical report, include:
- Tools used (e.g., ChatGPT, Copilot)
- Purpose per tool (planning, debugging, test ideation, language polishing)
- Verification method (manual review + test execution before accepting AI output)
- Reflection on limitations and independent decision-making
- Exported conversation logs as appendix evidence

---

## 12) Final Submission Checklist

- [ ] Public GitHub repository with visible and consistent commit history
- [ ] Fully runnable code that matches the oral demo version
- [ ] `README.md` complete and up to date
- [ ] `document/API Documentation.pdf` added and linked
- [ ] `document/Technical Report.pdf` added (max 5 pages, includes GenAI declaration)
- [ ] `document/slide.pptx` added or linked
- [ ] All references (dataset, libraries, tutorials) cited in report/slides
- [ ] Oral demo rehearsal completed (5-minute demo + 5-minute Q&A)
