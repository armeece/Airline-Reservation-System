import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Addison M - 11/30: Initialized extensions for SQLAlchemy, Flask, and MongoDB
db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'))

    # Addison M - 11/30: Configuration setup for Flask app and SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('instance/airline.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv("CSRF_SESSION_KEY", "default_csrf_secret_key")

    # Addison M - 11/30: Initialized Flask extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Addison M - 11/30: LoginManager configuration
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # Avoid circular import
        return User.query.get(int(user_id))

    # Addison M - 11/30: MongoDB integration setup
    app.config['MONGO_URI'] = os.getenv("MONGO_URI")

    def create_mongo_client():
        try:
            mongo_client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))
            mongo_client.admin.command('ping')  # Test connection
            print("Successfully connected to MongoDB!")
            return mongo_client
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return None

    mongo_client = create_mongo_client()
    mongo_db = mongo_client.get_database("Cluster7") if mongo_client else None

    # Addison M - 11/30: Blueprint registration
    from app.routes import main as main_blueprint
    from app.apis.auth_api import auth_blueprint
    from app.apis.booking_api import booking_blueprint
    from app.apis.flight_search_api import flight_search_blueprint
    from app.apis.seat_selection_api import seat_selection_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(booking_blueprint, url_prefix='/api/bookings')
    app.register_blueprint(flight_search_blueprint, url_prefix='/api/flights')
    app.register_blueprint(seat_selection_blueprint, url_prefix='/api/seats')

    return app
