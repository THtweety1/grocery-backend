from flask import Flask
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

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    return app