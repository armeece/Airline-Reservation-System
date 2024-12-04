# Original work by Dylaan Sooknanan - 11/30
# Updates and additional functionality by Addison M - 11/30

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Booking, Flight, db

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
    if not flight_id:
        return jsonify({"error": "Flight ID is required"}), 400

    # Fetch the flight using the given flight ID
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Optional: Prevent duplicate bookings
    existing_booking = Booking.query.filter_by(user_id=current_user.id, flight_id=flight_id).first()
    if existing_booking:
        return jsonify({"error": "You have already booked this flight"}), 400

    # Create and save the new booking
    new_booking = Booking(
        user_id=current_user.id,
        flight_id=flight_id,
        booking_time=db.func.now()  # Automatically sets the booking time
    )
    db.session.add(new_booking)
    db.session.commit()

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
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    # Handle cases where the user has no bookings
    if not bookings:
        return jsonify({"message": "No bookings found"}), 404

    # Format bookings data for response
    booking_list = [
        {
            "id": booking.id,
            "flight_id": booking.flight_id,
            "flight": {
                "origin": booking.flight.origin,
                "destination": booking.flight.destination,
                "departure_time": booking.flight.departure_time.isoformat(),
                "arrival_time": booking.flight.arrival_time.isoformat(),
                "price": booking.flight.price
            },
            "booking_time": booking.booking_time.isoformat()
        } for booking in bookings
    ]
    return jsonify({"bookings": booking_list}), 200

# ===================================
# Delete a Booking (Optional Feature)
# ===================================
@booking_blueprint.route('/bookings/<int:booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    """
    Delete a booking for the current user.
    """
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first()

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    db.session.delete(booking)
    db.session.commit()

    return jsonify({"message": "Booking deleted successfully"}), 200
