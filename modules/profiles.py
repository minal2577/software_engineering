from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import mongo

profiles_bp = Blueprint('profiles', __name__)

# Retrieve user profile
@profiles_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()

    # Find the user document; if it doesn’t exist, return a default profile structure
    user = mongo.db.users.find_one({"_id": user_id}) or {
        "username": "default_user",
        "email": "",
        "preferences": {},
        "recent_searches": []
    }

    user_data = {
        "username": user.get("username"),
        "email": user.get("email"),
        "preferences": user.get("preferences", {}),
        "recent_searches": user.get("recent_searches", [])
    }

    return jsonify(user_data), 200


# Update user preferences
@profiles_bp.route('/profile/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Use `$set` to add or update preferences in the user document
    mongo.db.users.update_one(
        {"_id": user_id},
        {"$set": {"preferences": data}},
        upsert=True  # upsert=True creates the document if it doesn't exist
    )

    return jsonify({"message": "Preferences updated successfully"}), 200


# Store recently searched products
@profiles_bp.route('/profile/history', methods=['POST'])
@jwt_required()
def add_to_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_name = data.get("product_name")

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    # Use `$push` to add product_name to the recent_searches array
    mongo.db.users.update_one(
        {"_id": user_id},
        {"$push": {"recent_searches": product_name}},
        upsert=True
    )

    return jsonify({"message": "Search history updated"}), 201


# Clear search history
@profiles_bp.route('/profile/history', methods=['DELETE'])
@jwt_required()
def clear_history():
    user_id = get_jwt_identity()

    # Set recent_searches to an empty array to clear history
    mongo.db.users.update_one(
        {"_id": user_id},
        {"$set": {"recent_searches": []}},
        upsert=True
    )

    return jsonify({"message": "Search history cleared"}), 200
