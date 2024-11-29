from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, Flight, db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.list_flights'))  # Redirect to flights or intended page
        return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
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
        return redirect(url_for('main.login'))  # Redirect to login page on successful registration
    return render_template('register.html')

@main.route('/flights')
def list_flights():
    """Display a list of flights."""
    flights = Flight.query.all()
    return render_template('flights.html', flights=flights)

@main.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for('main.home'))  # Redirect to home page after logout

@main.route('/book/<int:flight_id>')
def book_flight(flight_id):
    """Handle flight booking."""
    if not current_user.is_authenticated:
        return redirect(url_for('main.login', next=url_for('main.book_flight', flight_id=flight_id)))
    flight = Flight.query.get(flight_id)
    if not flight:
        return render_template('error.html', message="Flight not found.")  # Render an error page if flight doesn't exist
    # Placeholder for booking logic
    return f"Booking flight {flight_id}!"
