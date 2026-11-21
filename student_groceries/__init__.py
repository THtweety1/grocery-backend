from flask import Flask, jsonify
from config import config
from extensions import db, migrate


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = "default"

    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure models are registered with SQLAlchemy
    from student_groceries import models

    
    # Register blueprints
    from student_groceries.routes import main_bp
    from student_groceries.auth import auth_bp
    from student_groceries.users import users_bp
    from student_groceries.items import items_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(items_bp)
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            "error": "Bad request",
            "details": {"request": "The request could not be understood or was malformed."},
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "details": {"auth": "Authentication credentials were missing or invalid."},
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        return jsonify({
            "error": "Forbidden",
            "details": {"auth": "You do not have permission to access this resource."},
        }), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "error": "Not found",
            "details": {"route": "The requested resource or endpoint was not found."},
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "details": {"method": "The HTTP method is not allowed for this endpoint."},
        }), 405

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        return jsonify({
            "error": "Internal server error",
            "details": {"server": "An unexpected internal server error occurred."},
        }), 500

    return app