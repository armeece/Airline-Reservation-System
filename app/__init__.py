import os
from flask import Flask, session
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates")

    # Flask Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("CSRF_SESSION_KEY", "default_csrf_secret_key")
    app.config["SESSION_TYPE"] = "filesystem"  # Add session type for CSRF token handling

    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.get_user_by_id(user_id)

    # MongoDB Configuration
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not set in the .env file.")

    try:
        mongo_client = MongoClient(mongo_uri, server_api=ServerApi("1"))
        mongo_client.admin.command("ping")
        global mongo_db
        mongo_db = mongo_client.get_database("airline-reservation-system-g7")
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        mongo_db = None

    # Register Blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# Expose mongo_db for other modules
def get_mongo_db():
    return mongo_db
