# Nutrition & Recipe Analytics API (Coursework)

一个面向课程作业的高质量后端 API 项目，基于 FastAPI + SQLAlchemy，提供：
- 菜品与分类查询
- 套餐（Combo）完整 CRUD
- JWT 登录鉴权（Bearer Token）
- 营养分析与创意 analytics 端点
- 自动化测试（核心流程 + 边界场景）

---

## 1. Project Overview

本项目围绕“营养与食谱分析”主题实现 RESTful API，核心目标：
- 展示可维护的后端工程结构与数据库设计能力
- 展示完整 CRUD、认证、校验、错误处理
- 展示可解释、可演示的分析能力（protein density、分类统计）

技术栈：
- FastAPI（高性能、自动 OpenAPI 文档）
- SQLAlchemy ORM（关系建模与数据访问）
- SQLite / PostgreSQL（开发与部署兼容）
- JWT（`python-jose`）+ 密码哈希（`passlib`）
- Pytest（自动化测试）

---

## 2. Quick Start

### 2.1 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.2 配置环境变量

创建 `.env`（示例）：

```env
DATABASE_URL=sqlite:///./mcdonalds_nutrition.db
JWT_SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEMO_USERNAME=student
DEMO_PASSWORD=coursework123
```

> 生产环境请务必修改 `JWT_SECRET_KEY` 和演示账号密码。

### 2.3 启动服务

```bash
uvicorn app.main:app --reload
```

打开：
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 3. Authentication (JWT)

### 3.1 获取 Token

请求：

```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student&password=coursework123"
```

响应示例：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3.2 访问受保护端点

```bash
curl -X POST "http://127.0.0.1:8000/combos" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gym Combo",
    "description": "High protein lunch",
    "items": [{"item_id": 1, "quantity": 2}]
  }'
```

---

## 4. API Endpoints

### 4.1 Auth
- `POST /auth/token`：登录并获取 JWT
- `GET /auth/me`：获取当前用户信息（受保护）

### 4.2 Categories / Menu Items
- `GET /categories`
- `GET /categories/{category_id}/items`
- `GET /items`
- `GET /items/search?max_calories=500&min_protein=15`

### 4.3 Core CRUD: Combos
- `GET /combos`
- `GET /combos/{combo_id}`
- `POST /combos`（受保护）
- `PUT /combos/{combo_id}`（受保护）
- `DELETE /combos/{combo_id}`（受保护）

### 4.4 Analytics (Creativity)
- `GET /analytics/category-summary`  
  输出每个分类的平均热量、平均蛋白、条目数量
- `GET /analytics/combo-scoreboard`  
  按 `protein_density = total_protein / total_calories` 进行套餐排行榜

---

## 5. Validation & Error Handling

项目包含以下质量保障：
- 输入校验：字段长度、非负值、最小数量、分页参数上下界
- 业务校验：套餐重名冲突（409）、无效 item 引用（404）
- 鉴权错误：未认证/无效 token（401）
- 资源错误：不存在资源（404）
- 统一错误响应（包含 `detail` 与 `path`）
- 数据库异常和全局异常兜底处理（500）

---

## 6. Testing

运行测试：

```bash
pytest -q
```

当前覆盖场景包括：
- JWT 登录成功与失败
- 受保护端点的未认证访问
- Combo 完整 CRUD 流程
- 非法 item_id（404）
- 非法数量参数（422）
- analytics 端点正确性与排序逻辑

---

## 7. Suggested Repository Structure

```text
nutrition-recipe-api/
  app/
    database.py
    main.py
    models.py
    schemas.py
  tests/
    conftest.py
    test_api.py
  requirements.txt
  README.md
```

---

## 8. Deployment Notes

- 本地开发：SQLite（`sqlite:///./mcdonalds_nutrition.db`）
- 线上部署：建议 PostgreSQL（通过 `DATABASE_URL`）
- Render / Railway / PythonAnywhere 部署时：
  - 设置环境变量（JWT、数据库、演示账户）
  - 确保线上版本与口试演示一致

---

## 9. Marking Rubric Mapping (高分对照)

### Content (75%)
- **API Functionality & Implementation**  
  已实现核心资源完整 CRUD + 多个查询与分析端点
- **Code Quality & Architecture**  
  使用 ORM 关系建模、分层 schema、统一异常处理与鉴权依赖
- **Documentation**  
  Swagger 自动文档 + README 可执行说明（建议另补 API PDF 与技术报告 PDF）
- **Version Control & Deployment**  
  建议保持小步提交、语义化 commit message，并提供线上演示地址
- **Testing & Error Handling**  
  已有 pytest 自动化测试与边界场景
- **Creativity & GenAI**  
  通过组合营养评分与分类统计体现分析创造性（报告中需写明 GenAI 使用方法）

### Presentation (15%)
- 建议展示：系统架构图、ER 图、Swagger 截图、测试结果截图、部署链接、commit 历史

### Q&A (10%)
- 准备回答：JWT 选择理由、模型关系设计、错误码规范、测试策略、可扩展性方案

---

## 10. GenAI Declaration (for Technical Report)

你可以在技术报告中包含如下结构：
- 使用工具：例如 ChatGPT / Copilot
- 使用目的：需求拆解、接口设计建议、测试用例补全、文档润色
- 人工验证：所有 AI 建议均经本地运行、测试和人工审查
- 反思：AI 提升开发效率，但关键设计与最终取舍由作者完成

并附上部分对话导出日志作为附录材料。

---

## 11. Next Submission Checklist

- [ ] GitHub 仓库公开，commit 历史清晰
- [ ] README 完整（本文件）
- [ ] API 文档导出为 PDF 并放入仓库
- [ ] Technical Report（含 GenAI 声明）完成并转 PDF
- [ ] Slides 完成（5 分钟版本）
- [ ] 口试 demo 跑通（登录 + CRUD + analytics + 测试截图）
