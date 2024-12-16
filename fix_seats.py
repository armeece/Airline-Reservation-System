from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB Connection
client = MongoClient("mongodb+srv://jmase2212:Tafari1214@cluster7.bxmvh.mongodb.net/airline-reservation-system-g7?retryWrites=true&w=majority")
db = client['airline-reservation-system-g7']
flights_collection = db['flights']

# Function to Generate Correct Seat Data
def generate_seat_data():
    seats = []
    # First Class (Seats 1-10)
    for i in range(1, 11):
        seats.append({"seat_number": str(i), "seat_class": "First", "is_available": True})
    # Business Class (Seats 11-30)
    for i in range(11, 31):
        seats.append({"seat_number": str(i), "seat_class": "Business", "is_available": True})
    # Economy Class (Seats 31-60)
    for i in range(31, 61):
        seats.append({"seat_number": str(i), "seat_class": "Economy", "is_available": True})
    return seats

# Update Seat Data in All Flights
try:
    print("Updating seat data for all flights...")
    all_flights = flights_collection.find()  # Fetch all flights
    for flight in all_flights:
        flights_collection.update_one(
            {"_id": ObjectId(flight["_id"])},
            {"$set": {"seats": generate_seat_data()}}
        )
        print(f"Updated flight with ID: {flight['_id']}")
    print("All flights' seat data updated successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
