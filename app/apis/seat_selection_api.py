from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo_db

seat_selection_blueprint = Blueprint('seat_selection', __name__)

@seat_selection_blueprint.route('/seats/<flight_id>', methods=['GET'])
@login_required
def get_available_seats(flight_id):
    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    seats = flight.get("seats", [])
    booked_seats = bookings_collection.find({"flight_id": flight_id}).distinct("seat_number")

    for seat in seats:
        seat["is_available"] = seat["seat_number"] not in booked_seats

    return jsonify({"seats": seats}), 200

@seat_selection_blueprint.route('/seats/<flight_id>/select', methods=['POST'])
@login_required
def select_seat(flight_id):
    data = request.get_json()
    seat_number = data.get("seat_number")
    user_id = str(current_user.id)

    if not seat_number:
        return jsonify({"error": "Seat number is required"}), 400

    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    seat = next((s for s in flight.get("seats", []) if s["seat_number"] == seat_number), None)
    if not seat:
        return jsonify({"error": "Invalid seat number"}), 400

    existing_booking = bookings_collection.find_one({"flight_id": flight_id, "seat_number": seat_number})
    if existing_booking:
        return jsonify({"error": "Seat is already booked"}), 400

    booking = {
        "user_id": user_id,
        "flight_id": flight_id,
        "seat_number": seat_number,
        "status": "active",
        "timestamp": datetime.utcnow(),
        "price": flight.get("price", 0)
    }
    bookings_collection.insert_one(booking)

    flights_collection.update_one(
        {"_id": ObjectId(flight_id), "seats.seat_number": seat_number},
        {"$set": {"seats.$.is_available": False}}
    )

    return jsonify({"message": f"Seat {seat_number} booked successfully!"}), 200
