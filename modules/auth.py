# auth.py

from flask import Blueprint, request, jsonify, make_response, Flask
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, JWTManager
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Initialize Flask app and JWTManager
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a strong secret key
jwt = JWTManager(app)

# Initialize MongoDB client
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URI)
db = client['user_information']

# User registration route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_response(jsonify({"msg": "Username and password are required"}), 400)

    if db.users.find_one({"username": username}):
        return make_response(jsonify({"msg": "User  already exists"}), 400)

    hashed_password = generate_password_hash(password)
    db.users.insert_one({"username": username, "password": hashed_password})

    return jsonify({"msg": "User  registered successfully"}), 201

# User login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.users.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['_id']))
        refresh_token = create_refresh_token(identity=str(user['_id']))
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return make_response(jsonify({"msg": "Invalid username or password"}), 401)

# Test route to check if the user is authenticated
@auth_bp.route('/test_auth', methods=['GET'])
@jwt_required()
def test_auth():
    return jsonify({"status": "success", "message": "You are authenticated!"}), 200

# Refresh token route
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200

# Handle missing or invalid tokens
@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"msg": "Missing or invalid token"}), 401

# Handle expired tokens
@ jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return jsonify({"msg": "The token has expired"}), 401

# Handle token revocation
@jwt.needs_fresh_token_loader
def needs_fresh_token(jwt_header, jwt_payload):
    return jsonify({"msg": "The token is not fresh"}), 401

# Handle invalid tokens
@jwt.invalid_token_loader
def invalid_token_response(error):
    return jsonify({"msg": "Invalid token"}), 422