from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required

# Initialize your database
db = SQLAlchemy()

products_bp = Blueprint('products', __name__)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    aisle = db.Column(db.String(50), nullable=False)
    shelf_location = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)

# Create a product
@products_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        aisle=data['aisle'],
        shelf_location=data.get('shelf_location'),
        quantity=data['quantity']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"msg": "Product created successfully", "id": new_product.id}), 201

# Get all products
@products_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": product.id,
        "name": product.name,
        "aisle": product.aisle,
        "shelf_location": product.shelf_location,
        "quantity": product.quantity
    } for product in products]), 200

# Get a specific product
@products_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "aisle": product.aisle,
        "shelf_location": product.shelf_location,
        "quantity": product.quantity
    }), 200

# Update a product
@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.aisle = data.get('aisle', product.aisle)
    product.shelf_location = data.get('shelf_location', product.shelf_location)
    product.quantity = data.get('quantity', product.quantity)

    db.session.commit()
    return jsonify({"msg": "Product updated successfully"}), 200

# Delete a product
@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"msg": "Product deleted successfully"}), 200
