from flask_login import UserMixin
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo_db

class Role:
    def __init__(self, role_data):
        self.id = str(role_data.get("_id"))
        self.name = role_data.get("name")

    @staticmethod
    def get_roles_for_user(user_id):
        roles_collection = mongo_db.get_collection("roles")
        user_roles = roles_collection.find({"user_id": user_id})
        return [Role(role) for role in user_roles]

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data.get("username", "Unknown")
        self.email = user_data["email"]
        self.password_hash = user_data["password_hash"]
        self.created_at = user_data.get("created_at", datetime.utcnow())
        self.role = user_data.get("role", "user")  # Default role is 'user'
        self.roles = Role.get_roles_for_user(self.id)

    @staticmethod
    def get_user_by_email(email):
        users_collection = mongo_db.get_collection("users")
        user_data = users_collection.find_one({"email": email})
        return User(user_data) if user_data else None

    @staticmethod
    def get_user_by_id(user_id):
        users_collection = mongo_db.get_collection("users")
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    def is_admin(self):
        """
        Helper method to check if the user has an admin role.
        """
        return self.role == "admin"

class Flight:
    def __init__(self, flight_data):
        self.id = str(flight_data["_id"])
        self.origin = flight_data["origin"]
        self.destination = flight_data["destination"]
        self.departure_time = flight_data.get("departureTime")
        self.arrival_time = flight_data.get("arrivalTime")
        self.price = float(flight_data["price"])
        self.capacity = int(flight_data["availableSeats"])

    @staticmethod
    def get_all_flights():
        flights_collection = mongo_db.get_collection("flights")
        flight_data = flights_collection.find({})
        return [Flight(flight) for flight in flight_data]

    @staticmethod
    def get_flight_by_id(flight_id):
        flights_collection = mongo_db.get_collection("flights")
        flight_data = flights_collection.find_one({"_id": ObjectId(flight_id)})
        return Flight(flight_data) if flight_data else None

class Booking:
    def __init__(self, booking_data):
        self.id = str(booking_data["_id"])
        self.user_id = booking_data["user_id"]
        self.flight_id = booking_data["flight_id"]
        self.seat_number = booking_data["seat_number"]
        self.booking_time = booking_data.get("booking_time", datetime.utcnow())

    @staticmethod
    def create_booking(user_id, flight_id, seat_number):
        bookings_collection = mongo_db.get_collection("bookings")
        booking_data = {
            "user_id": user_id,
            "flight_id": flight_id,
            "seat_number": seat_number,
            "booking_time": datetime.utcnow(),
        }
        result = bookings_collection.insert_one(booking_data)
        return str(result.inserted_id)

    @staticmethod
    def get_bookings_for_user(user_id):
        bookings_collection = mongo_db.get_collection("bookings")
        bookings = bookings_collection.find({"user_id": user_id})
        return [Booking(booking) for booking in bookings]

    @staticmethod
    def get_booking_by_id(booking_id):
        bookings_collection = mongo_db.get_collection("bookings")
        booking_data = bookings_collection.find_one({"_id": ObjectId(booking_id)})
        return Booking(booking_data) if booking_data else None
