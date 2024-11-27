from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
import os
from bson.objectid import ObjectId  # Import ObjectId for MongoDB
from flask_cors import CORS  # Import CORS for cross-origin requests

# Create a Blueprint for shipment addresses
address_bp = Blueprint('address', __name__)
CORS(address_bp)  # Enable CORS for this blueprint

# Initialize MongoDB client
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URI)
db = client['user_information']  # Database name

# Add a shipment address
@address_bp.route('/address', methods=['POST'])
@jwt_required()
def add_address():
    data = request.get_json()
    print("Incoming data:", data)  # Log the incoming data

    # Extract address fields directly from the incoming data
    address = {
        "fullname": data.get('fullname'),  # Adjusted to match the frontend structure
        "address": data.get('address'),    # This is now a single string
        "city": data.get('city'),
        "state": data.get('state'),
        "zipCode": data.get('zipCode'),
        "country": data.get('country')
    }
    
    user_id = get_jwt_identity()  # Get the logged-in user's ID

    if not address.get('address'):
        return make_response(jsonify({"msg": "Address is required"}), 400)

    try:
        db.addresses.insert_one({"user_id": user_id, "address": address})
    except Exception as e:
        print("Error adding address:", str(e))  # Log the error
        return make_response(jsonify({"msg": "Error adding address", "error": str(e)}), 500)

    return jsonify({"msg": "Address added successfully"}), 201

# Get all addresses for the authenticated user
@address_bp.route('/address', methods=['GET'])
@jwt_required()
def get_addresses():
    user_id = get_jwt_identity()  # Get the logged-in user's ID
    addresses = list(db.addresses.find({"user_id": user_id}, {"_id": 0, "user_id": 0}))  # Exclude user_id from the response
    return jsonify(addresses), 200

# Update a shipment address
@address_bp.route('/address/<address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    data = request.get_json()
    new_address = {
        "fullname": data.get('fullname'),  # Adjusted to match the frontend structure
        "address": data.get('address'),
        "city": data.get('city'),
        "state": data.get('state'),
        "zipCode": data.get('zipCode'),
        "country": data.get('country')
    }
    
    user_id = get_jwt_identity()  # Get the logged-in user's ID

    if not new_address.get('address'):
        return make_response(jsonify({"msg": "New address is required"}), 400)

    result = db.addresses.update_one(
        {"_id": ObjectId(address_id), "user_id": user_id},  # Ensure the address belongs to the user
        {"$set": {"address": new_address}}
    )

    if result.matched_count == 0:
        return make_response(jsonify({"msg": "Address not found or does not belong to user"}), 404)

    return jsonify({"msg": "Address updated successfully"}), 200

# Delete a shipment address
@address_bp.route('/address/<address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()  # Get the logged-in user's ID
    result = db.addresses.delete_one({"_id": ObjectId(address_id), "user_id": user_id})  # Ensure the address belongs to the user

    if result.deleted_count == 0:
        return make_response(jsonify({"msg": "Address not found or does not belong to user"}), 404)

    return jsonify({"msg": "Address deleted successfully"}), 200