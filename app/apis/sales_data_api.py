from flask import Flask, jsonify
from app import mongo_db

app = Flask(__name__)

@app.route('/api/sales', methods=['GET'])
def get_sales_data():
    try:
        bookings_collection = mongo_db.get_collection('bookings')
        flights_collection = mongo_db.get_collection('flights')

        pipeline = [
            {"$lookup": {
                "from": "flights",
                "localField": "flight_id",
                "foreignField": "_id",
                "as": "flight_details"
            }},
            {"$unwind": "$flight_details"},
            {"$group": {
                "_id": "$flight_id",
                "total_bookings": {"$sum": 1},
                "total_revenue": {"$sum": "$flight_details.price"}
            }},
            {"$sort": {"total_revenue": -1}}
        ]

        sales_data = list(bookings_collection.aggregate(pipeline))

        response = [
            {
                "flight_id": str(data["_id"]),
                "total_bookings": data["total_bookings"],
                "total_revenue": float(data["total_revenue"]),
            }
            for data in sales_data
        ]

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
