from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, Flight, db
from app import bcrypt, mongo_db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Addison M - 11/30: Rendered the home page
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Addison M - 11/30: Implemented user login functionality
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # MongoDB Usage
        user_collection = mongo_db.get_collection('users')
        user = user_collection.find_one({"email": email}) if mongo_db else None

        if not user or not bcrypt.check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('main.login'))

        # Simulating LoginUser with SQLAlchemy User Model
        login_user(User.query.filter_by(email=email).first())
        flash('Welcome back!', 'success')
        return redirect(url_for('main.list_flights'))

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Addison M - 11/30: Implemented user registration with MongoDB
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # MongoDB Usage
        user_collection = mongo_db.get_collection('users')
        if user_collection.find_one({"email": email}):
            flash('Email is already registered. Please log in.', 'error')
            return redirect(url_for('main.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_collection.insert_one({"name": name, "email": email, "password_hash": hashed_password, "role": "customer"})

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/flights')
def list_flights():
    # Addison M - 11/30: Displayed a list of flights using SQLAlchemy
    flights = Flight.query.all()  # Using SQLAlchemy for flights
    return render_template('flights.html', flights=flights)

@main.route('/logout')
@login_required
def logout():
    # Addison M - 11/30: Implemented user logout functionality
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))
