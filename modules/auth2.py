from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# User registration
@auth_bp.route('/register', methods=['POST'])
def register():
    from app import mongo  # Local import to avoid circular import
    data = request.get_json()
    
    # Check if the user already exists
    if mongo.db.users.find_one({"username": data['username']}):
        return jsonify({"msg": "User already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(data['password'])
    new_user = {
        "username": data['username'],
        "password": hashed_password
    }

    mongo.db.users.insert_one(new_user)

    return jsonify({"msg": "User registered successfully"}), 201

# User login
@auth_bp.route('/login', methods=['POST'])
def login():
    from app import mongo  # Local import to avoid circular import
    data = request.get_json()
    user = mongo.db.users.find_one({"username": data['username']})

    if user and check_password_hash(user['password'], data['password']):
        # Create access token
        access_token = create_access_token(identity=str(user['_id']))  # Use user ID for identity
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401

# Protected route example
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify(msg="You have access to this protected route"), 200

