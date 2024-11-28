from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, bcrypt


class Flight(db.Model):
    """Flight model."""
    __tablename__ = "flights"

    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(100), nullable=False, index=True)
    destination = db.Column(db.String(100), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    bookings = db.relationship("Booking", backref="flight", lazy=True)

    def to_dict(self):
        """Serialize the Flight object to a dictionary."""
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "date": self.date.strftime('%Y-%m-%d'),
            "price": self.price,
        }

    @staticmethod
    def validate_flight_data(data):
        """Validate flight data before adding to the database."""
        required_fields = ["origin", "destination", "date", "price"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing or empty field: {field}")
        try:
            datetime.strptime(data["date"], '%Y-%m-%d')  # Validate date format
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")


class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default="Customer")  # Roles: "Admin" or "Customer"
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    bookings = db.relationship("Booking", backref="user", lazy=True)

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the given password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize the User object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }

    def is_admin(self):
        """Check if the user has an admin role."""
        return self.role.lower() == "admin"

    @staticmethod
    def validate_registration_data(data):
        """Validate user registration data before adding to the database."""
        required_fields = ["name", "email", "password"]
        for field in required_fields:
            if field not in data or not data[field].strip():
                raise ValueError(f"Missing or empty field: {field}")
        if User.query.filter_by(email=data["email"]).first():
            raise ValueError("Email is already registered.")


class Booking(db.Model):
    """Booking model."""
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey("flights.id"), nullable=False)
    seat_class = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Serialize the Booking object to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "flight_id": self.flight_id,
            "seat_class": self.seat_class,
            "price": self.price,
            "booking_date": self.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @staticmethod
    def validate_booking_data(data):
        """Validate booking data before adding to the database."""
        required_fields = ["user_id", "flight_id", "seat_class", "price"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing or empty field: {field}")
        if not isinstance(data["price"], (float, int)):
            raise ValueError("Price must be a number.")
