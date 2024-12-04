# Original work by Dylaan Sooknanan - 11/30
# Updates and additional functionality by Addison M - 11/30

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
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
    flight = flights_collection.find_one({"_id": flight_id})

    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Dummy logic for seat availability
    total_seats = flight.get("capacity", 100)
    booked_seats_count = bookings_collection.count_documents({"flight_id": flight_id})
    available_seats = total_seats - booked_seats_count

    return jsonify({
        "flight_id": flight_id,
        "total_seats": total_seats,
        "booked_seats": booked_seats_count,
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

    # Fetch booking data
    booking = bookings_collection.find_one({"_id": booking_id, "user_id": current_user.id})

    if not booking:
        return jsonify({"error": "Booking not found or unauthorized"}), 404

    # Ensure seat number is unique and not already taken
    existing_seat = bookings_collection.find_one({"flight_id": booking["flight_id"], "seat_number": seat_number})

    if existing_seat:
        return jsonify({"error": "Seat is already taken"}), 400

    # Update the booking with the selected seat
    result = bookings_collection.update_one(
        {"_id": booking_id},
        {"$set": {"seat_number": seat_number}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Failed to update booking"}), 500

    return jsonify({"message": "Seat selected successfully!"}), 200
