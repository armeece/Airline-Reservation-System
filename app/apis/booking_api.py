from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app import mongo_db

# ===================================
# Blueprint Initialization
# ===================================
booking_blueprint = Blueprint('booking', __name__)

# ===================================
# Create a New Booking
# ===================================
@booking_blueprint.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    """
    Create a new booking for the current user.
    """
    data = request.get_json()

    flight_id = data.get('flight_id')
    seat_number = data.get('seat_number')
    if not flight_id or not seat_number:
        return jsonify({"error": "Flight ID and seat number are required"}), 400

    # Fetch the flight using the given flight ID
    flights_collection = mongo_db.get_collection('flights')
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Prevent duplicate bookings
    bookings_collection = mongo_db.get_collection('bookings')
    existing_booking = bookings_collection.find_one({
        "user_id": current_user.id,
        "flight_id": flight_id
    })
    if existing_booking:
        return jsonify({"error": "You have already booked this flight"}), 400

    # Create and save the new booking in MongoDB
    new_booking = {
        "user_id": current_user.id,
        "flight_id": flight_id,
        "seat_number": seat_number,
        "booking_time": flight.get("departureTime")  # Defaulting to departure time for simplicity
    }
    bookings_collection.insert_one(new_booking)

    return jsonify({"message": "Booking created successfully!"}), 201

# ===================================
# Retrieve User's Bookings
# ===================================
@booking_blueprint.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    """
    Retrieve all bookings for the logged-in user.
    """
    bookings_collection = mongo_db.get_collection('bookings')
    flights_collection = mongo_db.get_collection('flights')

    # Fetch bookings for the current user
    bookings = list(bookings_collection.find({"user_id": current_user.id}))

    if not bookings:
        return jsonify({"message": "No bookings found"}), 404

    # Format bookings data for response
    booking_list = []
    for booking in bookings:
        flight = flights_collection.find_one({"_id": ObjectId(booking["flight_id"])})
        if not flight:
            continue  # Skip if the flight no longer exists

        booking_list.append({
            "id": str(booking["_id"]),
            "flight_id": booking["flight_id"],
            "seat_number": booking["seat_number"],
            "flight": {
                "origin": flight["origin"],
                "destination": flight["destination"],
                "departure_time": flight.get("departureTime") or flight.get("departure_time"),
                "arrival_time": flight.get("arrivalTime") or flight.get("arrival_time"),
                "price": float(flight["price"])
            },
            "booking_time": booking.get("booking_time")  # Stored as is from booking
        })

    return jsonify({"bookings": booking_list}), 200

# ===================================
# Delete a Booking (Optional Feature)
# ===================================
@booking_blueprint.route('/bookings/<booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    """
    Delete a booking for the current user.
    """
    bookings_collection = mongo_db.get_collection('bookings')

    # Delete the booking from MongoDB
    result = bookings_collection.delete_one({
        "_id": ObjectId(booking_id),
        "user_id": current_user.id
    })

    if result.deleted_count == 0:
        return jsonify({"error": "Booking not found or you are not authorized"}), 404

    return jsonify({"message": "Booking deleted successfully"}), 200
