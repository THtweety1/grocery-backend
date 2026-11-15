from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from extensions import db
from student_groceries.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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
