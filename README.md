# Grocery Backend

RESTful Flask backend API for a student grocery tracking application featuring JWT authentication, role-based admin access, item ownership enforcement, centralized validation, and paginated item listing.

## Quickstart (Fresh Clone)

```bash
git clone https://github.com/THtweety1/grocery-backend.git
cd grocery-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app student_groceries:create_app run --port 5055
```

## Smoke Test

In a second terminal:

```bash
curl -i http://127.0.0.1:5055/health
curl -i -X POST http://127.0.0.1:5055/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"eval_user","password":"Password123!"}'
```

## Environment Variables

- `FLASK_ENV` – `development` or `production` (default: `development`)
- `SECRET_KEY` – Flask session/app secret key
- `JWT_SECRET_KEY` – Secret key used to sign and verify JWT bearer tokens
- `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` – Token lifetime in minutes (default: `30`)
- `DATABASE_URL` – SQLAlchemy database URI (defaults to `sqlite:///dev.db`)
