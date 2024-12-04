from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# ===================================
# User-Role Association Table
# ===================================
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# ===================================
# Role Model
# ===================================
class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Define many-to-many relationship with User
    users = db.relationship(
        'User',
        secondary=user_roles,
        back_populates='roles'
    )

# ===================================
# User Model
# ===================================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define many-to-many relationship with Role
    roles = db.relationship(
        'Role',
        secondary=user_roles,
        back_populates='users'
    )

# ===================================
# Permission Model
# ===================================
class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

# ===================================
# Flight Model
# ===================================
class Flight(db.Model):
    __tablename__ = "flights"

    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

# ===================================
# Booking Model
# ===================================
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships
    user = db.relationship('User', backref=db.backref('bookings', lazy='dynamic'))
    flight = db.relationship('Flight', backref=db.backref('bookings', lazy='dynamic'))
