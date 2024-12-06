from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from app import mongo_db

flight_search_blueprint = Blueprint('flight_search', __name__)

@flight_search_blueprint.route('/flights', methods=['GET'])
def search_flights():
    origin = request.args.get('origin', "").strip()
    destination = request.args.get('destination', "").strip()
    departure_date = request.args.get('date')

    flights_collection = mongo_db.get_collection('flights')
    query = {}
    if origin:
        query["origin"] = {"$regex": f"^{origin}$", "$options": "i"}
    if destination:
        query["destination"] = {"$regex": f"^{destination}$", "$options": "i"}
    if departure_date:
        query["departureDate"] = departure_date

    flights = list(flights_collection.find(query))

    if not flights:
        return jsonify({"message": "No flights found matching the criteria"}), 404

    flight_list = [
        {
            "id": str(flight["_id"]),
            "origin": flight["origin"],
            "destination": flight["destination"],
            "departure_date": flight.get("departureDate"),
            "departure_time": flight.get("departureTime"),
            "arrival_time": flight.get("arrivalTime"),
            "price": flight.get("price"),
            "capacity": flight.get("availableSeats"),
        }
        for flight in flights
    ]
    return jsonify({"flights": flight_list}), 200

@flight_search_blueprint.route('/flights/<flight_id>', methods=['GET'])
def get_flight_details(flight_id):
    flights_collection = mongo_db.get_collection('flights')

    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    flight_details = {
        "id": str(flight["_id"]),
        "origin": flight["origin"],
        "destination": flight["destination"],
        "departure_date": flight.get("departureDate"),
        "departure_time": flight.get("departureTime"),
        "arrival_time": flight.get("arrivalTime"),
        "price": float(flight["price"]),
        "capacity": int(flight["availableSeats"]),
        "airline": flight.get("airline"),
        "class": flight.get("class"),
    }
    return jsonify(flight_details), 200
