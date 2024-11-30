from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Booking, Flight, db

seat_selection_blueprint = Blueprint('seat_selection', __name__)

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

    # Dummy logic for seat assignment
    # Assume each booking can have one seat, and seat_number validation is basic
    if not 1 <= int(seat_number) <= 100:
        return jsonify({"error": "Invalid seat number"}), 400

    # Store seat number (modify model if needed)
    booking.seat_class = seat_number  # Replace 'seat_class' with an actual seat column if required
    db.session.commit()

    return jsonify({"message": "Seat selected successfully!"}), 200
