from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app import mongo_db

# ===================================
# Blueprint Initialization
# ===================================
seat_selection_blueprint = Blueprint('seat_selection', __name__)

# ===================================
# Get Available Seats
# ===================================
@seat_selection_blueprint.route('/seats/<flight_id>', methods=['GET'])
@login_required
def get_available_seats(flight_id):
    """
    Retrieve available seats for a given flight.
    """
    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    # Fetch flight data
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})

    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Calculate seat availability
    total_seats = int(flight.get("availableSeats", 100))
    booked_seats = bookings_collection.find({"flight_id": flight_id}).distinct("seat_number")
    available_seats = [seat for seat in range(1, total_seats + 1) if str(seat) not in booked_seats]

    return jsonify({
        "flight_id": str(flight["_id"]),
        "total_seats": total_seats,
        "booked_seats": len(booked_seats),
        "available_seats": available_seats
    }), 200

# ===================================
# Select Seat
# ===================================
@seat_selection_blueprint.route('/seats/select', methods=['POST'])
@login_required
def select_seat():
    """
    Select a seat for a booking.
    """
    data = request.get_json()
    booking_id = data.get('booking_id')
    seat_number = data.get('seat_number')

    if not booking_id or not seat_number:
        return jsonify({"error": "Booking ID and seat number are required"}), 400

    bookings_collection = mongo_db.get_collection('bookings')

    # Validate booking ownership and existence
    booking = bookings_collection.find_one({
        "_id": ObjectId(booking_id),
        "user_id": str(current_user.id)
    })

    if not booking:
        return jsonify({"error": "Booking not found or unauthorized"}), 404

    # Ensure the seat is not already taken
    existing_seat = bookings_collection.find_one({
        "flight_id": booking["flight_id"],
        "seat_number": seat_number
    })

    if existing_seat:
        return jsonify({"error": "Seat is already taken"}), 400

    # Update the booking with the selected seat
    result = bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"seat_number": seat_number}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Failed to update booking"}), 500

    return jsonify({"message": "Seat selected successfully!"}), 200
