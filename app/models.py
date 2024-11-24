from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import bcrypt
from flask_login import UserMixin

db = SQLAlchemy()

class Flight(db.Model):
    """Flight model."""
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

class User(UserMixin, db.Model):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default="Customer")  # Role: "Admin" or "Customer"
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    bookings = db.relationship("Booking", backref="user", lazy=True)

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check hashed password."""
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
        """Check if the user is an admin."""
        return self.role.lower() == "admin"

class Booking(db.Model):
    """Booking model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey("flight.id"), nullable=False)
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
