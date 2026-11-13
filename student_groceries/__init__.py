from flask import Flask
from extensions import db, migrate  # <-- from root-level extensions.py


def create_app(config_name=None):
    app = Flask(__name__)

    # Base configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"

    # Environment-specific configuration
    if config_name == "testing":
        app.config["TESTING"] = True
    else:
        app.config["TESTING"] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from student_groceries.routes import main_bp

    app.register_blueprint(main_bp)
    from student_groceries import models  # ensures User is registered

    return app
