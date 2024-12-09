from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from app import bcrypt, mongo_db
from app.decorators import role_required
import os

# Blueprint Declaration
main = Blueprint('main', __name__)

# Helper: Simulate User for Flask-Login
class MongoUser:
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.role = user_data.get("role", "user")
        self.name = user_data.get("name", "Unknown")

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        user_collection = mongo_db.get_collection('users')
        user_data = user_collection.find_one({"_id": ObjectId(user_id)})
        return MongoUser(user_data) if user_data else None

# Ensure CSRF token setup before requests
@main.before_request
def ensure_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(24).hex()

# Routes Implementation
@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Submitted Data:", request.form)
        print("Session CSRF Token:", session.get('_csrf_token'))
        email = request.form.get('email')
        password = request.form.get('password')
        csrf_token = request.form.get('_csrf_token')

        if not csrf_token or csrf_token != session.get('_csrf_token'):
            flash('Invalid CSRF token.', 'error')
            return redirect(url_for('main.login'))

        user_collection = mongo_db.get_collection('users')
        user = user_collection.find_one({"email": email})
        if not user or not bcrypt.check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('main.login'))

        login_user(MongoUser(user))
        flash('Welcome back!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        csrf_token = request.form.get('_csrf_token')

        if not csrf_token or csrf_token != session.get('_csrf_token'):
            flash('Invalid CSRF token.', 'error')
            return redirect(url_for('main.register'))

        user_collection = mongo_db.get_collection('users')
        if user_collection.find_one({"email": email}):
            flash('Email is already registered. Please log in.', 'error')
            return redirect(url_for('main.register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_collection.insert_one({
            "name": name,
            "email": email,
            "password_hash": hashed_password,
            "role": "user"
        })
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.registration_success'))
    return render_template('register.html')

@main.route('/register/success')
def registration_success():
    return render_template('registration_success.html')

@main.route('/dashboard')
@login_required
def dashboard():
    bookings_collection = mongo_db.get_collection('bookings')
    flights_collection = mongo_db.get_collection('flights')

    user_bookings = bookings_collection.find({'user_id': ObjectId(current_user.id)})
    enriched_bookings = []
    for booking in user_bookings:
        flight = flights_collection.find_one({"_id": ObjectId(booking["flight_id"])})
        enriched_booking = {
            "seat_number": booking["seat_number"],
            "payment_status": booking["payment_status"],
            "flight": {
                "origin": flight.get("origin", "Unknown"),
                "destination": flight.get("destination", "Unknown"),
                "departureTime": flight.get("departureTime", "TBD"),
                "arrivalTime": flight.get("arrivalTime", "TBD"),
                "price": flight.get("price", "0"),
            } if flight else None
        }
        enriched_bookings.append(enriched_booking)

    return render_template('dashboard.html', bookings=enriched_bookings, user=current_user)

@main.route('/flights')
def list_flights():
    flights_collection = mongo_db.get_collection('flights')
    flights = list(flights_collection.find({}))

    formatted_flights = [
        {
            "id": str(flight["_id"]),
            "origin": flight.get("origin", "Unknown"),
            "destination": flight.get("destination", "Unknown"),
            "departure_time": flight.get("departureTime", "TBD"),
            "arrival_time": flight.get("arrivalTime", "TBD"),
            "price": float(flight.get("price", 0)),
        }
        for flight in flights
    ]

    return render_template('flights.html', flights=formatted_flights)

@main.route('/book/<flight_id>', methods=['GET', 'POST'])
@login_required
def book_flight(flight_id):
    flights_collection = mongo_db.get_collection('flights')
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})

    if not flight:
        flash('Flight not found.', 'error')
        return redirect(url_for('main.list_flights'))

    if request.method == 'POST':
        seat_number = request.form.get('seat_number')
        csrf_token = request.form.get('_csrf_token')

        if not csrf_token or csrf_token != session.get('_csrf_token'):
            flash('Invalid CSRF token.', 'error')
            return redirect(url_for('main.book_flight', flight_id=flight_id))

        if not seat_number or not seat_number.isdigit():
            flash('Please select a valid seat number.', 'error')
            return redirect(url_for('main.book_flight', flight_id=flight_id))

        bookings_collection = mongo_db.get_collection('bookings')
        existing_booking = bookings_collection.find_one({
            "flight_id": flight_id,
            "seat_number": seat_number
        })

        if existing_booking:
            flash("Seat is already booked. Please choose another seat.", "error")
            return redirect(url_for('main.book_flight', flight_id=flight_id))

        bookings_collection.insert_one({
            "user_id": current_user.id,
            "flight_id": flight_id,
            "seat_number": seat_number,
            "payment_status": "Pending"
        })

        flash("Booking successful! Please proceed to payment.", "success")
        return redirect(url_for('main.payment', flight_id=flight_id, seat_number=seat_number))

    return render_template('booking.html', flight={
        "id": str(flight["_id"]),
        "origin": flight.get("origin"),
        "destination": flight.get("destination"),
        "departure_time": flight.get("departureTime"),
        "arrival_time": flight.get("arrivalTime"),
        "price": flight.get("price"),
    })

@main.route('/payment/<flight_id>/<seat_number>', methods=['GET', 'POST'])
@login_required
def payment(flight_id, seat_number):
    flights_collection = mongo_db.get_collection('flights')
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})

    if not flight:
        flash('Flight not found.', 'error')
        return redirect(url_for('main.list_flights'))

    if request.method == 'POST':
        csrf_token = request.form.get('_csrf_token')
        if not csrf_token or csrf_token != session.get('_csrf_token'):
            flash('Invalid CSRF token.', 'error')
            return redirect(url_for('main.payment', flight_id=flight_id, seat_number=seat_number))

        card_number = request.form.get('card_number')
        expiration_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')

        if not card_number or not expiration_date or not cvv:
            flash('Please provide valid payment details.', 'error')
            return render_template('payment.html', flight=flight, seat_number=seat_number)

        bookings_collection = mongo_db.get_collection('bookings')
        bookings_collection.update_one(
            {"user_id": current_user.id, "flight_id": flight_id, "seat_number": seat_number},
            {"$set": {"payment_status": "Confirmed"}}
        )
        flash('Payment successful!', 'success')
        return redirect(url_for('main.payment_success'))

    return render_template('payment.html', flight=flight, seat_number=seat_number)

@main.route('/payment/success')
@login_required
def payment_success():
    return render_template('payment_success.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))
