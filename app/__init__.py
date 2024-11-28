import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Set configurations
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, '../instance/airline.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize extensions
    db.init_app(app)
    logger.info("SQLAlchemy initialized successfully.")
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Configure LoginManager
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Import blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    logger.info("App creation complete. Extensions initialized.")
    return app
