# products.py

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os

# Create a Blueprint for products
products_bp = Blueprint('products', __name__)

# Initialize MongoDB client
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')  # Use your actual MongoDB URI
client = MongoClient(MONGODB_URI)
db = client['user_information']  # Replace with your actual database name

# Search products route
@products_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q')  # Get the search query from the URL parameters
    if not query:
        return jsonify({"msg": "Query parameter 'q' is required"}), 400

    # Search for products that match the query in product_name or description
    products = db.products.find({
        "$or": [
            {"product_name": {"$regex": query, "$options": "i"}},  # Case-insensitive search
        ]
    })

    # Convert the cursor to a list of dictionaries
    results = []
    for product in products:
        product['_id'] = str(product['_id'])  # Convert ObjectId to string
        results.append(product)

    return jsonify(results), 200