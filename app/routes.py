from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from app import bcrypt, mongo_db
from app.forms import LoginForm, RegisterForm, BookingForm, PaymentForm
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

# Routes Implementation
@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_collection = mongo_db.get_collection('users')
        user = user_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            login_user(MongoUser(user))
            flash('Welcome back!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
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
    return render_template('register.html', form=form)

@main.route('/register/success')
def registration_success():
    return render_template('registration_success.html')

@main.route('/dashboard')
@login_required
def dashboard():
    bookings_collection = mongo_db.get_collection('bookings')
    flights_collection = mongo_db.get_collection('flights')

    # Ensure `current_user.id` is converted to ObjectId
    user_id = ObjectId(current_user.id)

    # Query all bookings for the current user
    user_bookings = bookings_collection.find({'user_id': user_id})

    # Enrich bookings with flight details
    enriched_bookings = []
    for booking in user_bookings:
        flight = flights_collection.find_one({"_id": ObjectId(booking["flight_id"])})
        if flight:
            enriched_bookings.append({
                "seat_number": booking["seat_number"],
                "payment_status": booking["payment_status"],
                "flight": {
                    "origin": flight.get("origin", "Unknown"),
                    "destination": flight.get("destination", "Unknown"),
                    "departure_time": flight.get("departureTime", "TBD"),
                    "arrival_time": flight.get("arrivalTime", "TBD"),
                    "price": float(flight.get("price", 0)),
                }
            })

    # Debug log
    print("Enriched Bookings for Dashboard:", enriched_bookings)

    return render_template(
        'dashboard.html',
        bookings=enriched_bookings,
        user=current_user
    )

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
    form = BookingForm()
    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    # Fetch the flight by ID
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        flash('Flight not found.', 'error')
        return redirect(url_for('main.list_flights'))

    # Convert `_id` for template usage
    flight["id"] = str(flight["_id"])

    if form.validate_on_submit():
        seat_number = form.seat_number.data

        # Ensure `current_user.id` is an `ObjectId`
        user_id = ObjectId(current_user.id)

        # Check if the seat is already booked
        existing_booking = bookings_collection.find_one({
            "flight_id": ObjectId(flight_id),
            "seat_number": seat_number
        })
        if existing_booking:
            flash("Seat is already booked. Please choose another seat.", "error")
            return redirect(url_for('main.book_flight', flight_id=flight_id))

        # Insert new booking
        bookings_collection.insert_one({
            "user_id": user_id,
            "flight_id": ObjectId(flight_id),
            "seat_number": seat_number,
            "payment_status": "Pending"
        })

        flash("Booking successful! Please proceed to payment.", "success")
        return redirect(url_for('main.payment', flight_id=flight_id, seat_number=seat_number))

    return render_template('booking.html', flight=flight, form=form)

@main.route('/payment/<flight_id>/<seat_number>', methods=['GET', 'POST'])
@login_required
def payment(flight_id, seat_number):
    form = PaymentForm()
    flights_collection = mongo_db.get_collection('flights')

    try:
        flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('main.list_flights'))

        flight["_id"] = str(flight["_id"])  # Convert for template usage

        if form.validate_on_submit():
            bookings_collection = mongo_db.get_collection('bookings')
            booking = bookings_collection.find_one({
                "user_id": current_user.id,
                "flight_id": ObjectId(flight_id),
                "seat_number": seat_number
            })

            if not booking:
                flash("Booking not found.", "error")
                return redirect(url_for('main.dashboard'))

            # Update booking with payment confirmation
            bookings_collection.update_one(
                {"user_id": current_user.id, "flight_id": ObjectId(flight_id), "seat_number": seat_number},
                {"$set": {"payment_status": "Confirmed"}}
            )
            flash('Payment successful!', 'success')
            return redirect(url_for('main.payment_success'))

    except Exception as e:
        flash(f"An error occurred during payment processing: {e}", "error")

    return render_template('payment.html', flight=flight, seat_number=seat_number, form=form)

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
