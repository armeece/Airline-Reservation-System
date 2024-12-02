# Original work by Dylaan Sooknanan - 11/30
# Updates and additional functionality by Addison M - 11/30

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Booking, Flight, db

booking_blueprint = Blueprint('booking', __name__)

@booking_blueprint.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking for the current user."""
    data = request.get_json()

    flight_id = data.get('flight_id')
    if not flight_id:
        return jsonify({"error": "Flight ID is required"}), 400

    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Check for duplicate bookings (optional)
    existing_booking = Booking.query.filter_by(user_id=current_user.id, flight_id=flight_id).first()
    if existing_booking:
        return jsonify({"error": "You have already booked this flight"}), 400

    new_booking = Booking(
        user_id=current_user.id,
        flight_id=flight_id
    )
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({"message": "Booking created successfully!"}), 201

@booking_blueprint.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    """Retrieve bookings for the logged-in user."""
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    if not bookings:
        return jsonify({"message": "No bookings found"}), 404

    booking_list = [
        {
            "id": booking.id,
            "flight_id": booking.flight_id,
            "flight": {
                "origin": booking.flight.origin,
                "destination": booking.flight.destination,
                "date": booking.flight.date.isoformat(),
                "price": booking.flight.price
            },
            "booking_date": booking.booking_date.isoformat()
        } for booking in bookings
    ]
    return jsonify({"bookings": booking_list}), 200
