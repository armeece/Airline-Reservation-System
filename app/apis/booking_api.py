from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app import mongo_db

booking_blueprint = Blueprint('booking', __name__)

@booking_blueprint.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json()
    flight_id = data.get('flight_id')
    seat_number = data.get('seat_number')
    if not flight_id or not seat_number:
        return jsonify({"error": "Flight ID and seat number are required"}), 400

    flights_collection = mongo_db.get_collection('flights')
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    bookings_collection = mongo_db.get_collection('bookings')
    existing_booking = bookings_collection.find_one({
        "user_id": current_user.id,
        "flight_id": flight_id
    })
    if existing_booking:
        return jsonify({"error": "You have already booked this flight"}), 400

    new_booking = {
        "user_id": current_user.id,
        "flight_id": flight_id,
        "seat_number": seat_number,
        "booking_time": flight.get("departureTime")
    }
    bookings_collection.insert_one(new_booking)
    return jsonify({"message": "Booking created successfully!"}), 201

@booking_blueprint.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings_collection = mongo_db.get_collection('bookings')
    flights_collection = mongo_db.get_collection('flights')

    bookings = list(bookings_collection.find({"user_id": current_user.id}))

    if not bookings:
        return jsonify({"message": "No bookings found"}), 404

    booking_list = []
    for booking in bookings:
        flight = flights_collection.find_one({"_id": ObjectId(booking["flight_id"])})
        if not flight:
            continue

        booking_list.append({
            "id": str(booking["_id"]),
            "flight_id": booking["flight_id"],
            "seat_number": booking["seat_number"],
            "flight": {
                "origin": flight["origin"],
                "destination": flight["destination"],
                "departure_time": flight.get("departureTime"),
                "arrival_time": flight.get("arrivalTime"),
                "price": float(flight["price"])
            },
            "booking_time": booking.get("booking_time")
        })

    return jsonify({"bookings": booking_list}), 200

@booking_blueprint.route('/bookings/<booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    bookings_collection = mongo_db.get_collection('bookings')
    result = bookings_collection.delete_one({
        "_id": ObjectId(booking_id),
        "user_id": current_user.id
    })

    if result.deleted_count == 0:
        return jsonify({"error": "Booking not found or you are not authorized"}), 404

    return jsonify({"message": "Booking deleted successfully"}), 200
