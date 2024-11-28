from flask import Blueprint, jsonify, request, render_template, redirect
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/flights')  # Redirect to flights page on successful login
        return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered!")
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')  # Redirect to login page on successful registration
    return render_template('register.html')

@main.route('/flights')
@login_required
def list_flights():
    # Test data for now
    flights = [
        {"id": 1, "origin": "New York", "destination": "Los Angeles", "date": "2024-11-30", "price": 300.0},
        {"id": 2, "origin": "Chicago", "destination": "Miami", "date": "2024-12-01", "price": 200.0},
    ]
    return render_template('flights.html', flights=flights)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')  # Redirect to home page after logout
