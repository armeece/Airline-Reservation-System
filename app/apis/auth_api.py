# Original work by Dylaan Sooknanan - 11/30
# Updates and additional functionality by Addison M - 11/30

from flask import Blueprint, jsonify, request
from app.models import User, db
from app import bcrypt, mongo_db

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Name, email, and password are required"}), 400

    # MongoDB Usage
    user_collection = mongo_db.get_collection('users')
    if user_collection.find_one({"email": data['email']}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user_collection.insert_one({
        "name": data['name'],
        "email": data['email'],
        "password_hash": hashed_password,
        "role": "customer"
    })

    return jsonify({"message": "User registered successfully!"}), 201
