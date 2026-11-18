### Current Project Summary: `grocery-backend`

- **What the app does:**
  A Flask REST API backend for a student grocery list manager that lets authenticated users register, log in, manage their profile, and create/manage their own personal grocery items.

- **Core resource:**
  `GroceryItem` (`grocery_items` table) — a grocery list item belonging to a single authenticated user, with fields:
  - `id` (`Integer`, PK)
  - `user_id` (`Integer`, FK → `users.id`, `nullable=False`)
  - `name` (`String(120)`, `nullable=False`)
  - `quantity` (`Integer`, `nullable=False`, default `1`)
  - `category` (`String(80)`, `nullable=True`)
  - `notes` (`Text`, `nullable=True`)
  - `purchased` (`Boolean`, `nullable=False`, default `False`)
  - `created_at` (`DateTime`, UTC timestamp, `nullable=False`)

- **How users/auth currently work:**
  - `POST /auth/register` hashes passwords with `generate_password_hash` and creates a `User` (`role="user"` by default).
  - `POST /auth/login` verifies passwords with `check_password_hash` and signs an `HS256` JWT containing `"sub"` (user ID), `"role"`, and `"exp"`.
  - A `@token_required` decorator validates `Authorization: Bearer <token>`, loads `g.current_user` (`401` if missing/invalid), and enforces role/ownership checks (`403`/`404` in JSON).

- **Where models and routes live:**
  - `student_groceries/__init__.py` — `create_app()` factory, `.env` config loading, model registration, and blueprint registration
  - `extensions.py` — `db` (`SQLAlchemy`) and `migrate` (`Flask-Migrate`) instances
  - `student_groceries/models.py` — SQLAlchemy models (`User` and `GroceryItem` with `user`/`items` relationship and `to_dict()` serializer)
  - `student_groceries/auth.py` — `auth_bp` (`/auth/register`, `/auth/login`, `/auth/me`) and `@token_required`
  - `student_groceries/users.py` — `users_bp` (`/users`, `/users/me`)
  - `student_groceries/routes.py` — `main_bp` (`/health`) and upcoming user-scoped grocery item routes (or `student_groceries/items.py`)
  - `migrations/` — Alembic database migration scripts (`0ba648350396_add_grocery_items_table.py` applied via `flask db upgrade`)

- **Core resource endpoint plan (`GroceryItem`):**
  All endpoints require `@token_required` and scope access strictly to `g.current_user.id`:
  - `POST /items` — Create a new grocery item owned by the current user (`201 Created`).
  - `GET /items` — List all grocery items belonging to the current user (`200 OK`).
  - `GET /items/<int:item_id>` — Retrieve a single grocery item if owned by the current user (`403` or `404` in JSON error shape if owned by another user or missing).
  - `PATCH /items/<int:item_id>` — Update fields (`name`, `quantity`, `category`, `notes`, `purchased`) on the current user's item (`403`/`404` otherwise).
  - `DELETE /items/<int:item_id>` — Delete the current user's item (`200`/`204` or `403`/`404` otherwise).