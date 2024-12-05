from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
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
    origin = request.args.get('origin', "").strip()
    destination = request.args.get('destination', "").strip()
    departure_date = request.args.get('date')  # Format: YYYY-MM-DD

    # MongoDB flight collection
    flights_collection = mongo_db.get_collection('flights')

    # Build the query dynamically
    query = {}
    if origin:
        query["origin"] = {"$regex": f"^{origin}$", "$options": "i"}  # Case-insensitive exact match
    if destination:
        query["destination"] = {"$regex": f"^{destination}$", "$options": "i"}  # Case-insensitive exact match
    if departure_date:
        query["departureDate"] = departure_date

    # Query MongoDB for flights matching criteria
    flights = list(flights_collection.find(query))

    # Handle no flights found
    if not flights:
        return jsonify({"message": "No flights found matching the criteria"}), 404

    # Format the response
    flight_list = [
    {
        "id": str(flight["_id"]),  # MongoDB `_id` converted to string
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

# ===================================
# Get Flight Details by ID
# ===================================
@flight_search_blueprint.route('/flights/<flight_id>', methods=['GET'])
def get_flight_details(flight_id):
    """
    Retrieve flight details by flight ID.
    """
    flights_collection = mongo_db.get_collection('flights')

    # Fetch the flight by ID
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Format the response
    flight_details = {
        "id": str(flight["_id"]),
        "origin": flight["origin"],
        "destination": flight["destination"],
        "departure_date": flight.get("departureDate"),
        "departure_time": flight.get("departureTime") or flight.get("departure_time"),
        "arrival_time": flight.get("arrivalTime") or flight.get("arrival_time"),
        "price": float(flight["price"]),
        "capacity": int(flight["availableSeats"]),
        "airline": flight.get("airline"),
        "class": flight.get("class"),
    }
    return jsonify(flight_details), 200
