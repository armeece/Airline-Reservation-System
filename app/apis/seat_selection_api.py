from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo_db

seat_selection_blueprint = Blueprint('seat_selection', __name__)

# GET available seats
@seat_selection_blueprint.route('/<flight_id>/seats', methods=['GET'])
@login_required
def get_available_seats(flight_id):
    """
    Fetch available seats for a specific flight.
    """
    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    try:
        flight_id_obj = ObjectId(flight_id)
    except Exception:
        return jsonify({"error": "Invalid flight ID format"}), 400

    try:
        flight = flights_collection.find_one({"_id": flight_id_obj})
        if not flight:
            return jsonify({"error": "Flight not found"}), 404

        booked_seats = bookings_collection.find({"flight_id": flight_id_obj}).distinct("seat_number")
        seats = flight.get("seats", [])

        for seat in seats:
            seat["is_available"] = str(seat["seat_number"]) not in booked_seats

        return jsonify({"seats": seats}), 200

    except Exception as e:
        print(f"Error fetching seats for flight {flight_id}: {e}")
        return jsonify({"error": "An error occurred while fetching seats"}), 500

# POST: Select seat
@seat_selection_blueprint.route('/<flight_id>/seats/select', methods=['POST'])
@login_required
def select_seat(flight_id):
    """
    Allow a user to reserve a specific seat for a flight.
    """
    data = request.get_json()
    seat_number = str(data.get("seat_number", "").strip())
    user_id = str(current_user.id)

    if not seat_number:
        return jsonify({"error": "Seat number is required"}), 400

    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    try:
        flight_id_obj = ObjectId(flight_id)
    except Exception:
        return jsonify({"error": "Invalid flight ID format"}), 400

    try:
        seat_query = {"_id": flight_id_obj, "seats": {"$elemMatch": {"seat_number": seat_number, "is_available": True}}}
        update_query = {"$set": {"seats.$.is_available": False}}
        result = flights_collection.update_one(seat_query, update_query)

        if result.modified_count == 0:
            return jsonify({"error": "Seat is not available or already reserved"}), 400

        booking = {
            "user_id": ObjectId(user_id),
            "flight_id": flight_id_obj,
            "seat_number": seat_number,
            "status": "active",
            "timestamp": datetime.utcnow(),
            "price": 0  # Placeholder price
        }
        bookings_collection.insert_one(booking)

        return jsonify({"message": f"Seat {seat_number} booked successfully!"}), 200

    except Exception as e:
        print(f"Error during seat selection: {e}")
        return jsonify({"error": "An error occurred while selecting the seat"}), 500
