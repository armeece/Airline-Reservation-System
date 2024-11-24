from flask import Blueprint, jsonify, request
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, db
from app import login_manager

main = Blueprint('main', __name__)

# Define the user_loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return jsonify(message="Welcome to the Airline Reservation System!")

@main.route('/flights')
@login_required
def list_flights():
    return jsonify(message=f"Flights page: List of flights for user {current_user.name}.")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify(status="error", message="Email already registered!")

        # Create a new user
        new_user = User(name=name, email=email, role="Customer")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify(status="success", message="Registration successful! Please log in.")
    
    return jsonify(message="Registration page. Send a POST request with name, email, and password.")

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify(status="success", message="Login successful!")

        return jsonify(status="error", message="Invalid credentials. Please try again.")
    
    return jsonify(message="Login page. Send a POST request with email and password.")

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(status="success", message="You have been logged out.")
