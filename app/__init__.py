from flask import Flask
from .extensions import db, login_manager, migrate, mail
from .routes import main
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'main.login'

    # Register Blueprint
    app.register_blueprint(main)

    # Create database tables only if they don't exist
    with app.app_context():
        db.create_all()  # This will only create tables that don't exist yet

    return app
