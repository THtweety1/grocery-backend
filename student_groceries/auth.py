from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from student_groceries.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({"error": "Missing or invalid token"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
            user = db.session.get(User, int(payload["sub"]))
            if not user:
                return jsonify({"error": "User not found"}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except (jwt.InvalidTokenError, KeyError, ValueError):
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


@auth_bp.post("/register")
def register():
    if not request.is_json:
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be valid JSON."}
        }), 400

    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    details = {}
    if not isinstance(username, str) or not username.strip():
        details["username"] = "Username is required and must be a non-empty string."
    elif len(username.strip()) > 80:
        details["username"] = "Username must be 80 characters or fewer."

    if not isinstance(password, str) or not password.strip():
        details["password"] = "Password is required and must be a non-empty string."
    elif len(password) < 8:
        details["password"] = "Password must be at least 8 characters long."

    if details:
        return jsonify({
            "error": "Validation failed",
            "details": details
        }), 400

    clean_username = username.strip()

    existing_user = User.query.filter_by(username=clean_username).first()
    if existing_user:
        return jsonify({
            "error": "Username already exists",
            "details": {"username": f"The username '{clean_username}' is already taken."}
        }), 409

    new_user = User(
        username=clean_username,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
        }
    }), 201


@auth_bp.post("/login")
def login():
    if not request.is_json:
        return jsonify({"error": "Invalid credentials"}), 401

    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid credentials"}), 401

    user = User.query.filter_by(username=username.strip()).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    jwt_secret = current_app.config["JWT_SECRET_KEY"]
    lifetime_minutes = current_app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"]

    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=lifetime_minutes),
    }

    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return jsonify({"access_token": token}), 200


@auth_bp.get("/me")
@token_required
def get_me():
    return jsonify({
        "id": g.current_user.id,
        "username": g.current_user.username,
        "created_at": g.current_user.created_at.isoformat() if g.current_user.created_at else None,
    }), 200