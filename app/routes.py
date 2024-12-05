from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
from app import bcrypt, mongo_db

# Blueprint Declaration
main = Blueprint('main', __name__)

# Helper: Simulate User for Flask-Login
class MongoUser:
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.role = user_data.get("role", "customer")
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

# Route: Home Page
@main.route('/')
def home():
    return render_template('home.html')

# Route: Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from MongoDB
        user_collection = mongo_db.get_collection('users')
        user = user_collection.find_one({"email": email})

        # Validate credentials
        if not user or not bcrypt.check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('main.login'))

        # Log in user
        login_user(MongoUser(user))
        flash('Welcome back!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

# Route: Registration
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email already exists
        user_collection = mongo_db.get_collection('users')
        if user_collection.find_one({"email": email}):
            flash('Email is already registered. Please log in.', 'error')
            return redirect(url_for('main.register'))

        # Hash password and insert user into MongoDB
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_collection.insert_one({
            "name": name,
            "email": email,
            "password_hash": hashed_password,
            "role": "customer"
        })

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.registration_success'))

    return render_template('register.html')

# Route: Registration Success
@main.route('/register/success')
def registration_success():
    return render_template('registration_success.html')

# Route: User Dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Route: List Flights
@main.route('/flights')
def list_flights():
    flights_collection = mongo_db.get_collection('flights')
    flights = list(flights_collection.find({}))

    # Format flights for rendering
    formatted_flights = [
        {
            "id": str(flight["_id"]),
            "origin": flight["origin"],
            "destination": flight["destination"],
            "departure_time": flight.get("departureTime") or flight.get("departure_time"),
            "arrival_time": flight.get("arrivalTime") or flight.get("arrival_time"),
            "price": float(flight["price"]),
            "capacity": int(flight["availableSeats"]),
        }
        for flight in flights
    ]

    return render_template('flights.html', flights=formatted_flights)

# Route: Book Flight
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

        if not seat_number:
            flash('Please select a valid seat number.', 'error')
            return redirect(url_for('main.book_flight', flight_id=flight_id))

        # Redirect to the payment page with the seat number
        return redirect(url_for('main.payment', flight_id=flight_id, seat_number=seat_number))

    return render_template('booking.html', flight=flight)

# Route: Booking Confirmation
@main.route('/confirmation')
@login_required
def booking_confirmation():
    return render_template('booking_confirmation.html')

# Route: Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

# Route: Payment Page
@main.route('/payment/<flight_id>', methods=['GET', 'POST'])
@login_required
def payment(flight_id):
    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    seat_number = request.args.get('seat_number')  # Fetch seat number from query parameters

    if not flight:
        flash('Flight not found.', 'error')
        return redirect(url_for('main.list_flights'))

    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')

        # Basic validation for all fields
        if not card_number or not expiry_date or not cvv or not seat_number:
            flash('All fields (seat number and payment details) are required.', 'error')
            return redirect(url_for('main.payment', flight_id=flight_id, seat_number=seat_number))

        # Check if the seat is still available
        existing_booking = bookings_collection.find_one({
            "flight_id": flight_id,
            "seat_number": seat_number
        })
        if existing_booking:
            flash('Seat is already booked. Please choose another seat.', 'error')
            return redirect(url_for('main.book_flight', flight_id=flight_id))

        # Insert booking and confirm payment
        bookings_collection.insert_one({
            "user_id": current_user.id,
            "flight_id": flight_id,
            "seat_number": seat_number,
            "payment_status": "Confirmed"
        })

        flash('Payment successful! Your booking is confirmed.', 'success')
        return redirect(url_for('main.booking_confirmation'))

    return render_template('payment.html', flight=flight, seat_number=seat_number)
