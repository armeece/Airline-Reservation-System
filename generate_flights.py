import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
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
classes = ["Economy", "Business", "First"]

# Function to generate random flights
def generate_random_flights(count=25):
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
            "availableSeats": random.randint(50, 200),
            "class": random.choice(classes)
        }
        flights.append(flight)
    return flights

# Generate and insert flights into MongoDB
try:
    flights = generate_random_flights()
    flights_collection.insert_many(flights)
    print(f"{len(flights)} flights have been added to MongoDB!")
except Exception as e:
    print(f"An error occurred: {e}")
