import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

# Initialize Flask extensions
db = SQLAlchemy()  # SQLAlchemy for local database
bcrypt = Bcrypt()  # Bcrypt for password hashing
csrf = CSRFProtect()  # CSRF protection
login_manager = LoginManager()  # User session management
migrate = Migrate()  # Database migration support

# Addison M - Application Factory
def create_app():
    # Flask Application Setup
    app = Flask(__name__, template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'))

    # Flask Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('instance/airline.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv("CSRF_SESSION_KEY", "default_csrf_secret_key")

    # Initialize Flask extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # LoginManager Configuration
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # User loader for session management
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # Avoid circular import
        return User.query.get(int(user_id))

    # MongoDB Setup
    password = quote_plus("Tafari1214")  # Encode special characters
    app.config['MONGO_URI'] = f"mongodb+srv://jmase2212:{password}@cluster7.bxmvh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster7"

    def create_mongo_client():
        """
        Creates a MongoDB client and verifies connection.
        """
        try:
            mongo_client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))
            mongo_client.admin.command('ping')  # Test the connection
            print("Successfully connected to MongoDB!")
            return mongo_client
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return None

    # Create MongoDB Client and Database Reference
    mongo_client = create_mongo_client()
    global mongo_db
    mongo_db = mongo_client.get_database("airline-reservation-system-g7") if mongo_client else None

    # Blueprint Registration
    from app.routes import main as main_blueprint
    from app.apis.auth_api import auth_blueprint
    from app.apis.booking_api import booking_blueprint
    from app.apis.flight_search_api import flight_search_blueprint
    from app.apis.seat_selection_api import seat_selection_blueprint
    
    app.register_blueprint(main_blueprint, url_prefix='/')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # Register once
    app.register_blueprint(booking_blueprint, url_prefix='/api/bookings')
    app.register_blueprint(flight_search_blueprint, url_prefix='/api/flights')
    app.register_blueprint(seat_selection_blueprint, url_prefix='/api/seats')

    return app
