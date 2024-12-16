import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables (optional if credentials are stored locally)
load_dotenv()

# MongoDB connection
client = MongoClient("mongodb+srv://jmase2212:Tafari1214@cluster7.bxmvh.mongodb.net/airline-reservation-system-g7?retryWrites=true&w=majority")
db = client['airline-reservation-system-g7']
flights_collection = db['flights']

# Data for random generation
airports = [
    "New York (JFK)", "Los Angeles (LAX)", "Chicago (ORD)", "Miami (MIA)",
    "San Francisco (SFO)", "Seattle (SEA)", "Houston (IAH)", "Atlanta (ATL)"
]
airlines = ["Delta Airlines", "American Airlines", "United Airlines", "Southwest Airlines"]

# Generate seat data
def generate_seat_data():
    seats = []
    # First Class (1-10)
    seats.extend([{"seat_number": str(i), "seat_class": "First", "is_available": True} for i in range(1, 11)])
    # Business Class (11-30)
    seats.extend([{"seat_number": str(i), "seat_class": "Business", "is_available": True} for i in range(11, 31)])
    # Economy Class (31-60)
    seats.extend([{"seat_number": str(i), "seat_class": "Economy", "is_available": True} for i in range(31, 61)])
    return seats

# Function to generate random flights
def generate_random_flights(count=10):
    flights = []
    for _ in range(count):
        origin = random.choice(airports)
        destination = random.choice([a for a in airports if a != origin])
        departure_time = datetime.utcnow() + timedelta(days=random.randint(1, 30))
        arrival_time = departure_time + timedelta(hours=random.randint(2, 6))
        flight = {
            "origin": origin,
            "destination": destination,
            "departureTime": departure_time,  # Store as native datetime
            "arrivalTime": arrival_time,     # Store as native datetime
            "price": round(random.uniform(100, 1000), 2),
            "airline": random.choice(airlines),
            "availableSeats": 60,  # Total seats
            "seats": generate_seat_data()  # Detailed seat data
        }
        flights.append(flight)
    return flights

# Clear old flights and insert new ones
try:
    print("Deleting old flight data...")
    flights_collection.delete_many({})  # Deletes all documents in the collection

    print("Generating new flight data...")
    new_flights = generate_random_flights(count=10)

    flights_collection.insert_many(new_flights)
    print(f"{len(new_flights)} flights have been added to MongoDB successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
