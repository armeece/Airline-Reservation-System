from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Booking, Flight, db

seat_selection_blueprint = Blueprint('seat_selection', __name__)  # Define the blueprint here

@seat_selection_blueprint.route('/seats/<int:flight_id>', methods=['GET'])
@login_required
def get_available_seats(flight_id):
    """Retrieve available seats for a given flight."""
    flight = Flight.query.get(flight_id)

    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Dummy logic for seat availability
    total_seats = 100
    booked_seats = Booking.query.filter_by(flight_id=flight_id).count()
    available_seats = total_seats - booked_seats

    return jsonify({
        "flight_id": flight_id,
        "total_seats": total_seats,
        "booked_seats": booked_seats,
        "available_seats": available_seats
    }), 200

@seat_selection_blueprint.route('/seats/select', methods=['POST'])
@login_required
def select_seat():
    """Select a seat for a booking."""
    data = request.get_json()
    booking_id = data.get('booking_id')
    seat_number = data.get('seat_number')

    if not booking_id or not seat_number:
        return jsonify({"error": "Booking ID and seat number are required"}), 400

    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != current_user.id:
        return jsonify({"error": "Booking not found or unauthorized"}), 404

    # Ensure seat number is unique and not already taken
    if Booking.query.filter_by(flight_id=booking.flight_id, seat_number=seat_number).first():
        return jsonify({"error": "Seat is already taken"}), 400

    booking.seat_number = seat_number
    db.session.commit()

    return jsonify({"message": "Seat selected successfully!"}), 200
