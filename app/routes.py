from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from app import bcrypt, mongo_db
from app.forms import LoginForm, RegisterForm, BookingForm, PaymentForm
import random
import re

# Utility Function for Payment Processing
def mock_payment_gateway(card_number, expiry_date, cvv):
    def luhn_checksum(card_num):
        total = 0
        reverse_digits = card_num[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0

    if not re.match(r"^\d{16}$", card_number) or not luhn_checksum(card_number):
        return {"success": False, "message": "Invalid card number."}

    try:
        exp_month, exp_year = map(int, expiry_date.split("/"))
        expiry_datetime = datetime.strptime(f"{exp_month:02d}/{exp_year:02d}", "%m/%y")
        if expiry_datetime < datetime.now():
            return {"success": False, "message": "Card has expired."}
    except ValueError:
        return {"success": False, "message": "Invalid expiry date format."}

    if not re.match(r"^\d{3}$", cvv):
        return {"success": False, "message": "Invalid CVV."}

    if random.choice([True, False]):
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        return {"success": True, "message": "Payment successful!", "transaction_id": transaction_id}
    else:
        failure_reasons = ["Insufficient funds", "Transaction declined", "Network error"]
        return {"success": False, "message": random.choice(failure_reasons)}

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

# Flight Details Page
@main.route('/flight/<flight_id>/details', methods=['GET'])
def flight_details(flight_id):
    """
    Display flight details and available seat classes.
    """
    flight = mongo_db.flights.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        flash("Flight not found.", "error")
        return redirect(url_for('main.list_flights'))

    return render_template('flight_details.html', flight=flight)

# Updated Routes for Seat Selection (Author: James Mason)
@main.route('/flight/<flight_id>/select-seat', methods=['GET'])
def seat_selection_page(flight_id):
    """
    Render the seat selection page for the specified flight.
    """
    return render_template('seat_selection.html', flight_id=flight_id)

@main.route('/api/flights/<flight_id>/seats', methods=['GET', 'POST'])
def seat_selection_api(flight_id):
    """
    API for fetching and booking seats for a flight.
    - GET: Return seat map and flight details.
    - POST: Book a selected seat.

    Author: James Mason (Updated 2024-12-15)
    """
    if not mongo_db:
        return jsonify({"error": "Database connection not established"}), 500

    flight = mongo_db.flights.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    if request.method == 'POST':
        data = request.json
        selected_seat_number = data.get("seat_number")
        user_id = current_user.id  # Fetch logged-in user ID
        if not selected_seat_number:
            return jsonify({"error": "seat_number is required"}), 400

        seat = next((s for s in flight.get("seats", []) if s["seat_number"] == selected_seat_number), None)
        if seat and seat["is_available"]:
            mongo_db.flights.update_one(
                {"_id": ObjectId(flight_id), "seats.seat_number": selected_seat_number},
                {"$set": {"seats.$.is_available": False}}
            )
            booking = {
                "user_id": user_id,
                "flight_id": flight_id,
                "seat_number": selected_seat_number,
                "status": "active",
                "timestamp": datetime.utcnow(),
                "price": flight.get("price", 0)
            }
            mongo_db.bookings.insert_one(booking)
            return jsonify({"message": f"Seat {selected_seat_number} booked successfully!"}), 200
        else:
            return jsonify({"error": "Seat not available"}), 400

    return jsonify({
        "flight_id": str(flight["_id"]),
        "origin": flight["origin"],
        "destination": flight["destination"],
        "seats": flight.get("seats", [])
    }), 200

from flask import render_template

@main.route('/payment/<flight_id>/<seat_number>', methods=['GET', 'POST'])
@login_required
def payment(flight_id, seat_number):
    """
    Display the payment page and handle payment processing.
    """
    form = PaymentForm()
    flight = mongo_db.flights.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        flash("Flight not found.", "error")
        return redirect(url_for("main.list_flights"))

    if request.method == "POST" and form.validate_on_submit():
        card_number = form.card_number.data
        expiry_date = form.expiry_date.data
        cvv = form.cvv.data

        # Process payment using mock gateway
        payment_result = mock_payment_gateway(card_number, expiry_date, cvv)

        if payment_result["success"]:
            # Update the booking status in MongoDB
            mongo_db.bookings.update_one(
                {"flight_id": flight_id, "seat_number": seat_number, "user_id": str(current_user.id)},
                {"$set": {"payment_status": "Paid", "transaction_id": payment_result["transaction_id"]}}
            )
            flash("Payment successful!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash(payment_result["message"], "error")

    return render_template("payment.html", flight=flight, seat_number=seat_number, form=form)

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
            return redirect(request.args.get('next') or url_for('main.dashboard'))
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

    user_id = ObjectId(current_user.id)
    user_bookings = bookings_collection.find({'user_id': user_id})

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

    return render_template(
        'dashboard.html',
        bookings=enriched_bookings,
        user=current_user
    )

@main.route('/flights')
def list_flights():
    flights_collection = mongo_db.get_collection('flights')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')
    travel_class = request.args.get('class')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = {}
    if origin:
        query['origin'] = {"$regex": origin, "$options": "i"}
    if destination:
        query['destination'] = {"$regex": destination, "$options": "i"}
    if date:
        try:
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
            price_query["$gte"] = float(min_price)
        if max_price:
            price_query["$lte"] = float(max_price)
        query['price'] = price_query

    flights = list(flights_collection.find(query))
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

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))
