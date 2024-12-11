# app/api/__init__.py
from .auth_api import auth_blueprint
from .booking_api import booking_blueprint
from .flight_search_api import flight_search_blueprint
from .seat_selection_api import seat_selection_blueprint

def register_blueprints(app):
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(booking_blueprint, url_prefix='/api/bookings')
    app.register_blueprint(flight_search_blueprint, url_prefix='/api/flights')
    app.register_blueprint(seat_selection_blueprint, url_prefix='/api/seats')
