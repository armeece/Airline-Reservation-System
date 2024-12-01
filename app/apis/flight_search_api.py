from flask import Blueprint, jsonify, request
from app.models import Flight, db

flight_search_blueprint = Blueprint('flight_search', __name__)

@flight_search_blueprint.route('/flights', methods=['GET'])
def search_flights():
    """Search for flights based on origin, destination, and date."""
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')  # Format: YYYY-MM-DD

    query = Flight.query

    if origin:
        query = query.filter(Flight.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Flight.destination.ilike(f"%{destination}%"))
    if date:
        query = query.filter(Flight.date == date)

    flights = query.all()

    if not flights:
        app.logger.info("No flights found for given criteria")
        return jsonify({"message": "No flights found matching the criteria"}), 404

    flight_list = [
        {
            "id": flight.id,
            "origin": flight.origin,
            "destination": flight.destination,
            "date": flight.date.isoformat(),
            "price": flight.price
        } for flight in flights
    ]
    return jsonify({"flights": flight_list}), 200