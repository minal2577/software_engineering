from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Your MongoDB URI (consider using environment variables for sensitive information)
MONGODB_URI = 'mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

# Load environment variables (optional)
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', MONGODB_URI)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_default_jwt_secret')  # Change this for production

# Initialize MongoDB client
client = MongoClient(app.config['MONGODB_URI'])
db = client['user_information']  # Replace with your actual database name

# Initialize JWT manager
jwt = JWTManager(app)

# Root route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the User Authentication API!"}), 200

# User registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_response(jsonify({"msg": "Username and password are required"}), 400)

    # Check if user already exists
    if db.users.find_one({"username": username}):
        return make_response(jsonify({"msg": "User already exists"}), 400)

    # Hash the password and store the user
    hashed_password = generate_password_hash(password)
    db.users.insert_one({"username": username, "password": hashed_password})

    return jsonify({"msg": "User registered successfully"}), 201

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.users.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return make_response(jsonify({"msg": "Invalid username or password"}), 401)

# Test route to check if the user is authenticated
@app.route('/test_auth', methods=['GET'])
@jwt_required()
def test_auth():
    return jsonify({"status": "success", "message": "You are authenticated!"}), 200

# Refresh token route
@app.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)