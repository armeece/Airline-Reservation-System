import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from pymongo import MongoClient
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
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY")
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = False

    # Validate Required Environment Variables
    required_env_vars = ["SECRET_KEY", "WTF_CSRF_SECRET_KEY", "MONGO_URI"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Initialize Flask extensions
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Flask-Login Configuration
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.routes import MongoUser
        return MongoUser.get(user_id)

    # MongoDB Configuration
    mongo_uri = os.getenv("MONGO_URI")
    try:
        mongo_client = MongoClient(mongo_uri)
        global mongo_db
        mongo_db = mongo_client.get_database()
        mongo_client.admin.command("ping")
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise RuntimeError("Failed to connect to MongoDB. Ensure your MONGO_URI is correct and accessible.")

    # Register Blueprints
    from app.routes import main
    from app.apis.seat_selection_api import seat_selection_blueprint  # Import the API blueprint

    app.register_blueprint(main)
    app.register_blueprint(seat_selection_blueprint, url_prefix="/api")  # Register with /api prefix

    return app

# Expose MongoDB client for other modules
def get_mongo_db():
    return mongo_db
