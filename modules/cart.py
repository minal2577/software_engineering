from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
import os
from bson.objectid import ObjectId

# Create a Blueprint for the cart
cart_bp = Blueprint('cart', __name__)

# Initialize MongoDB client
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URI)
db = client['user_information']  # Replace with your actual database name

# Add an item to the cart
@cart_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    print("Received data", data)
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)  # Default quantity to 1 if not provided
    user_id = get_jwt_identity()  # Get the logged-in user's ID

    if not item_id or quantity <= 0:
        return make_response(jsonify({"msg": "Item ID and quantity are required"}), 400)

    # Check if the item already exists in the cart
    existing_item = db.carts.find_one({"user_id": user_id, "item_id": item_id})

    if existing_item:
        # Update the quantity if the item already exists
        db.carts.update_one(
            {"_id": existing_item["_id"]},
            {"$set": {"quantity": existing_item["quantity"] + quantity}}
        )
    else:
        # Add a new item to the cart
        db.carts.insert_one({"user_id": user_id, "item_id": item_id, "quantity": quantity})

    return jsonify({"msg": "Item added to cart successfully"}), 201

# Get all items in the cart for the authenticated user
@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()  # Get the logged-in user's ID
    print(f"Retrieved User ID: {user_id}")  # Debugging output

    # Query the cart items for the specific user
    cart_items = list(db.carts.find({"user_id": user_id}, {"_id": 0, "user_id": 0}))  # Exclude user_id from the response
    print(f"Cart Items: {cart_items}")  # Debugging output

    if not cart_items:
        return jsonify({"message": "Cart is empty"}), 404  # Return a message if the cart is empty

    detailed_cart_items = []

    for item in cart_items:
        product_id = item['item_id']
        print(f"Processing Product ID: {product_id}")  # Debugging output
        
        try:
            # Convert product_id to ObjectId since it's stored as an ObjectId in the database
            product_id_obj = ObjectId(product_id)
            # Fetch product details from the products collection
            product_details = db.product.find_one({"_id": product_id_obj}, {"_id": 0})
        except Exception as e:
            print(f"Error fetching product details for {product_id}: {e}")
            continue

        if product_details:
            detailed_item = {
                "product_name": product_details.get('product_name'),
                "price": product_details.get('price'),
                "description": product_details.get('description'),
                "quantity": item.get('quantity')
            }
            detailed_cart_items.append(detailed_item)

    return jsonify(detailed_cart_items), 200

# Update the quantity of an item in the cart
@cart_bp.route('/cart/<item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    data = request.get_json()
    new_quantity = data.get('quantity')
    user_id = get_jwt_identity()  # Get the logged-in user's ID

    if new_quantity is None or new_quantity <= 0:
        return make_response(jsonify({"msg": "New quantity is required and must be greater than 0"}), 400)

    result = db.carts.update_one(
        {"user_id": user_id, "item_id": item_id},
        {"$set": {"quantity": new_quantity}}
    )

    if result.matched_count == 0:
        return make_response(jsonify({"msg": "Item not found in cart"}), 404)

    return jsonify({"msg": "Item quantity updated successfully"}), 200

# Delete an item from the cart
@cart_bp.route('/cart/<item_id>', methods=['DELETE'])
@jwt_required()
def delete_cart_item(item_id):
    user_id = get_jwt_identity()  # Get the logged-in user's ID
    result = db.carts.delete_one({"user_id": user_id, "item_id": item_id})

    if result.deleted_count == 0:
        return make_response(jsonify({"msg": "Item not found in cart"}), 404)

    return jsonify({"msg": "Item removed from cart successfully"}), 200