from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo_db

seat_selection_blueprint = Blueprint('seat_selection', __name__)

# GET available seats
@seat_selection_blueprint.route('/seats/<flight_id>', methods=['GET'])
@login_required
def get_available_seats(flight_id):
    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    try:
        flight_id_obj = ObjectId(flight_id)  # Validate ObjectId
    except Exception:
        return jsonify({"error": "Invalid flight ID format"}), 400

    try:
        flight = flights_collection.find_one({"_id": flight_id_obj})
        if not flight:
            return jsonify({"error": "Flight not found"}), 404

        booked_seats = bookings_collection.find({"flight_id": flight_id_obj}).distinct("seat_number")
        seats = flight.get("seats", [])
        if not seats:
            return jsonify({"error": "No seats data available for this flight"}), 404

        for seat in seats:
            seat["is_available"] = seat["seat_number"] not in booked_seats

        return jsonify({"seats": seats}), 200

    except Exception as e:
        print(f"Error fetching seats for flight {flight_id}: {e}")
        return jsonify({"error": "An error occurred while fetching seats"}), 500


# POST: Select seat
@seat_selection_blueprint.route('/seats/<flight_id>/select', methods=['POST'])
@login_required
def select_seat(flight_id):
    data = request.get_json()
    seat_number = str(data.get("seat_number", "").strip())
    user_id = str(current_user.id)

    # Debugging Logs
    print("---- Debugging Info ----")
    print(f"Flight ID: {flight_id}")
    print(f"Request Payload: {data}")
    print(f"User ID: {user_id}")
    print("------------------------")

    if not seat_number:
        return jsonify({"error": "Seat number is required"}), 400

    flights_collection = mongo_db.get_collection('flights')
    bookings_collection = mongo_db.get_collection('bookings')

    try:
        flight_id_obj = ObjectId(flight_id)  # Validate ObjectId
    except Exception:
        return jsonify({"error": "Invalid flight ID format"}), 400

    try:
        # Fetch flight
        flight = flights_collection.find_one({"_id": flight_id_obj})
        if not flight:
            return jsonify({"error": "Flight not found"}), 404

        # Validate seat number
        seats = flight.get("seats", [])
        if not seats:
            return jsonify({"error": "No seat data available"}), 404

        seat_index = next((i for i, seat in enumerate(seats) if seat["seat_number"] == seat_number), None)
        if seat_index is None:
            return jsonify({"error": "Invalid seat number"}), 400

        # Check seat availability
        if not seats[seat_index].get("is_available", True):
            return jsonify({"error": "Seat is not available"}), 400

        # Check for duplicate booking
        existing_booking = bookings_collection.find_one({
            "flight_id": flight_id_obj,
            "seat_number": seat_number
        })
        if existing_booking:
            return jsonify({"error": "Seat is already booked"}), 400

        # Mark seat as unavailable in the flight document
        update_field = f"seats.{seat_index}.is_available"
        result = flights_collection.update_one(
            {"_id": flight_id_obj},
            {"$set": {update_field: False}}
        )
        print(f"MongoDB Update Result: {result.raw_result}")

        if result.modified_count == 0:
            return jsonify({"error": "Failed to update seat availability"}), 500

        # Add booking to database
        booking = {
            "user_id": ObjectId(user_id),
            "flight_id": flight_id_obj,
            "seat_number": seat_number,
            "status": "active",
            "timestamp": datetime.utcnow(),
            "price": flight.get("price", 0)
        }
        bookings_collection.insert_one(booking)
        print(f"Seat {seat_number} successfully booked for user {user_id}")

        return jsonify({"message": f"Seat {seat_number} booked successfully!"}), 200

    except Exception as e:
        print(f"Error during seat selection for flight {flight_id}: {e}")
        return jsonify({"error": "An error occurred while selecting the seat"}), 500
