from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime, timedelta  # Import for date handling
from app import bcrypt, mongo_db
from app.forms import LoginForm, RegisterForm, BookingForm, PaymentForm
import os
import random  # Import for randomizing payment success or failure

# Utility Function for Payment Processing
def mock_payment_gateway(card_number, expiry_date, cvv):
    """
    Simulates a payment gateway for processing payments.
    Args:
        card_number (str): Credit card number
        expiry_date (str): Expiry date in MM/YY format
        cvv (str): CVV code (3 digits)

    Returns:
        dict: A dictionary containing success status and a message.
    """
    # Validate card details
    if len(card_number) != 16 or not card_number.isdigit():
        return {"success": False, "message": "Invalid card number."}
    if not expiry_date or not cvv or len(cvv) != 3 or not cvv.isdigit():
        return {"success": False, "message": "Invalid card details."}
    
    # Simulate success or failure
    success = random.choice([True, False])  # Randomize success or failure
    return {
        "success": success,
        "message": "Payment successful!" if success else "Payment failed. Insufficient funds.",
    }

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

    # Fetch query parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')  # Format: YYYY-MM-DD
    travel_class = request.args.get('class')  # Economy, Business, First
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    # Build query dynamically
    query = {}
    if origin:
        query['origin'] = {"$regex": origin, "$options": "i"}  # Case-insensitive partial match
    if destination:
        query['destination'] = {"$regex": destination, "$options": "i"}  # Case-insensitive partial match
    if date:
        try:
            # Convert date string to a range of datetime objects
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            next_day = date_obj + timedelta(days=1)
            query['departureTime'] = {"$gte": date_obj, "$lt": next_day}
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('main.list_flights'))
    if travel_class:
        query['class'] = travel_class
    if min_price or max_price:
        price_query = {}
        if min_price:
            try:
                price_query["$gte"] = float(min_price)
            except ValueError:
                flash("Invalid minimum price.", "error")
                return redirect(url_for('main.list_flights'))
        if max_price:
            try:
                price_query["$lte"] = float(max_price)
            except ValueError:
                flash("Invalid maximum price.", "error")
                return redirect(url_for('main.list_flights'))
        query['price'] = price_query

    # Fetch filtered flights
    flights = list(flights_collection.find(query))

    # Format the flights for rendering
    formatted_flights = [
        {
            "id": str(flight["_id"]),
            "origin": flight.get("origin", "Unknown"),
            "destination": flight.get("destination", "Unknown"),
            "departure_time": flight.get("departureTime", "TBD"),
            "arrival_time": flight.get("arrivalTime", "TBD"),
            "price": float(flight.get("price", 0)),
            "class": flight.get("class", "Unknown"),
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
        # Fetch the flight details
        flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('main.list_flights'))

        # Convert flight ID for template usage
        flight["_id"] = str(flight["_id"])

        if form.validate_on_submit():
            # Extract payment details from form
            card_number = form.card_number.data
            expiry_date = form.expiry_date.data
            cvv = form.cvv.data

            # Simulate payment processing
            payment_result = mock_payment_gateway(card_number, expiry_date, cvv)

            # Handle payment failure
            if not payment_result["success"]:
                flash(payment_result["message"], "error")
                return render_template('payment.html', flight=flight, seat_number=seat_number, form=form)

            # Payment success: Update booking with confirmation
            bookings_collection = mongo_db.get_collection('bookings')
            booking = bookings_collection.find_one({
                "user_id": ObjectId(current_user.id),
                "flight_id": ObjectId(flight_id),
                "seat_number": seat_number
            })

            if not booking:
                flash("Booking not found.", "error")
                return redirect(url_for('main.dashboard'))

            bookings_collection.update_one(
                {
                    "user_id": ObjectId(current_user.id),
                    "flight_id": ObjectId(flight_id),
                    "seat_number": seat_number
                },
                {"$set": {"payment_status": "Confirmed"}}
            )
            flash(payment_result["message"], "success")
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
