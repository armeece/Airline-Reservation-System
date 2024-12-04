# Original work by Dylaan Sooknanan - 11/30
# Updates and additional functionality by Addison M - 11/30

from flask import Blueprint, jsonify, request
from app import mongo_db

# ===================================
# Blueprint Initialization
# ===================================
flight_search_blueprint = Blueprint('flight_search', __name__)

# ===================================
# Search for Flights
# ===================================
@flight_search_blueprint.route('/flights', methods=['GET'])
def search_flights():
    """
    Search for flights based on origin, destination, and date.
    """
    # Retrieve search parameters from the request
    origin = request.args.get('origin', "").lower()
    destination = request.args.get('destination', "").lower()
    date = request.args.get('date')  # Format: YYYY-MM-DD

    # MongoDB flight collection
    flights_collection = mongo_db.get_collection('flights')

    # Build the query dynamically
    query = {}
    if origin:
        query["origin"] = {"$regex": origin, "$options": "i"}
    if destination:
        query["destination"] = {"$regex": destination, "$options": "i"}
    if date:
        query["departureDate"] = date

    # Query MongoDB for flights matching criteria
    flights = list(flights_collection.find(query))

    # Handle no flights found
    if not flights:
        return jsonify({"message": "No flights found matching the criteria"}), 404

    # Format the response
    flight_list = [
        {
            "id": str(flight["_id"]),
            "origin": flight["origin"],
            "destination": flight["destination"],
            "departure_date": flight["departureDate"],
            "departure_time": flight["departureTime"],
            "arrival_time": flight["arrivalTime"],
            "price": flight["price"],
            "capacity": flight["availableSeats"],
        }
        for flight in flights
    ]
    return jsonify({"flights": flight_list}), 200
