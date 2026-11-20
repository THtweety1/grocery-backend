from flask import Blueprint, g, jsonify, request
from extensions import db
from student_groceries.auth import token_required
from student_groceries.models import GroceryItem

items_bp = Blueprint("items", __name__, url_prefix="/items")


def get_owned_item_or_404(item_id):
    item = db.session.get(GroceryItem, item_id)
    if item is None or item.user_id != g.current_user.id:
        return None, (jsonify({"error": "Item not found"}), 404)
    return item, None


@items_bp.post("")
@token_required
def create_item():
    if not request.is_json:
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be valid JSON."}
        }), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be a JSON object."}
        }), 400

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "error": "Validation failed",
            "details": {"name": "Name is required and must be a non-empty string."}
        }), 400

    clean_name = name.strip()
    if len(clean_name) > 120:
        return jsonify({
            "error": "Validation failed",
            "details": {"name": "Name must be 120 characters or fewer."}
        }), 400

    quantity = data.get("quantity", 1)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        return jsonify({
            "error": "Validation failed",
            "details": {"quantity": "Quantity must be a positive integer."}
        }), 400

    category = data.get("category")
    if category is not None and not isinstance(category, str):
        return jsonify({
            "error": "Validation failed",
            "details": {"category": "Category must be a string."}
        }), 400

    notes = data.get("notes")
    if notes is not None and not isinstance(notes, str):
        return jsonify({
            "error": "Validation failed",
            "details": {"notes": "Notes must be a string."}
        }), 400

    purchased = data.get("purchased", False)
    if not isinstance(purchased, bool):
        return jsonify({
            "error": "Validation failed",
            "details": {"purchased": "Purchased must be a boolean."}
        }), 400

    item = GroceryItem(
        user_id=g.current_user.id,
        name=clean_name,
        quantity=quantity,
        category=category.strip() if isinstance(category, str) else None,
        notes=notes.strip() if isinstance(notes, str) else None,
        purchased=purchased,
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


@items_bp.get("")
@token_required
def list_items():
    items = (
        GroceryItem.query.filter_by(user_id=g.current_user.id)
        .order_by(GroceryItem.id.asc())
        .all()
    )
    return jsonify([item.to_dict() for item in items]), 200


@items_bp.get("/<int:item_id>")
@token_required
def get_item(item_id):
    item, error_response = get_owned_item_or_404(item_id)
    if error_response is not None:
        return error_response

    return jsonify(item.to_dict()), 200


@items_bp.patch("/<int:item_id>")
@token_required
def update_item(item_id):
    item, error_response = get_owned_item_or_404(item_id)
    if error_response is not None:
        return error_response

    if not request.is_json:
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be valid JSON."}
        }), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "error": "Validation failed",
            "details": {"body": "Request body must be a JSON object."}
        }), 400

    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Validation failed",
                "details": {"name": "Name must be a non-empty string."}
            }), 400
        clean_name = name.strip()
        if len(clean_name) > 120:
            return jsonify({
                "error": "Validation failed",
                "details": {"name": "Name must be 120 characters or fewer."}
            }), 400
        item.name = clean_name

    if "quantity" in data:
        quantity = data["quantity"]
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            return jsonify({
                "error": "Validation failed",
                "details": {"quantity": "Quantity must be a positive integer."}
            }), 400
        item.quantity = quantity

    if "category" in data:
        category = data["category"]
        if category is not None and not isinstance(category, str):
            return jsonify({
                "error": "Validation failed",
                "details": {"category": "Category must be a string."}
            }), 400
        item.category = category.strip() if isinstance(category, str) else None

    if "notes" in data:
        notes = data["notes"]
        if notes is not None and not isinstance(notes, str):
            return jsonify({
                "error": "Validation failed",
                "details": {"notes": "Notes must be a string."}
            }), 400
        item.notes = notes.strip() if isinstance(notes, str) else None

    if "purchased" in data:
        purchased = data["purchased"]
        if not isinstance(purchased, bool):
            return jsonify({
                "error": "Validation failed",
                "details": {"purchased": "Purchased must be a boolean."}
            }), 400
        item.purchased = purchased

    db.session.commit()
    return jsonify(item.to_dict()), 200


@items_bp.delete("/<int:item_id>")
@token_required
def delete_item(item_id):
    item, error_response = get_owned_item_or_404(item_id)
    if error_response is not None:
        return error_response

    db.session.delete(item)
    db.session.commit()
    return "", 204
