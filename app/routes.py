from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, Flight, db

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
            return redirect(url_for('main.list_flights'))
        return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered!")
        try:
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception as e:
            return render_template('register.html', error=f"Error: {e}")
    return render_template('register.html')

@main.route('/flights')
def list_flights():
    flights = Flight.query.all()
    return render_template('flights.html', flights=flights)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/book/<int:flight_id>')
@login_required
def book_flight(flight_id):
    flight = Flight.query.get(flight_id)
    if not flight:
        return render_template('error.html', message="Flight not found.")
    return f"Booking flight {flight_id}!"
