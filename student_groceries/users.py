from flask import Blueprint, g, jsonify, request
from extensions import db
from student_groceries.security import token_required
from student_groceries.models import User

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("")
@token_required
def list_users():
    if g.current_user.role != "admin":
        return jsonify({
            "error": "Forbidden",
            "details": {"role": "Admin privileges are required to access this resource."}
        }), 403

    users = User.query.order_by(User.id.asc()).all()
    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]
    }), 200


@users_bp.patch("/me")
@token_required
def update_user_profile():
    if not request.is_json:
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be valid JSON."}
        }), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be a non-empty JSON object."}
        }), 400

    # Explicit profile allowlist: only fields listed here may be modified via PATCH /users/me.
    # Keep restricted fields (id, password_hash, created_at, role) excluded so future columns stay protected.
    allowed_fields = {"username"}
    disallowed = sorted(set(data.keys()) - allowed_fields)
    if disallowed:
        return jsonify({
            "error": "Disallowed fields in request",
            "details": {
                "allowed_fields": sorted(allowed_fields),
                "disallowed_fields": disallowed,
            }
        }), 400

    if "username" in data:
        username = data["username"]
        if not isinstance(username, str) or not username.strip():
            return jsonify({
                "error": "Validation failed",
                "details": {"username": "Username must be a non-empty string."}
            }), 400

        clean_username = username.strip()
        if len(clean_username) > 80:
            return jsonify({
                "error": "Validation failed",
                "details": {"username": "Username must be 80 characters or fewer."}
            }), 400

        existing = User.query.filter(
            User.username == clean_username,
            User.id != g.current_user.id,
        ).first()
        if existing:
            return jsonify({
                "error": "Username already exists",
                "details": {"username": f"The username '{clean_username}' is already taken."}
            }), 409

        g.current_user.username = clean_username

    db.session.commit()

    return jsonify({
        "id": g.current_user.id,
        "username": g.current_user.username,
        "created_at": g.current_user.created_at.isoformat() if g.current_user.created_at else None,
    }), 200