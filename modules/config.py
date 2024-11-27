from flask import Flask
from flask_pymongo import PyMongo
import os

# Step 1: Initialize PyMongo
mongo = PyMongo()

# Step 2: Define the application factory
def create_app():
    app = Flask(__name__)

    # Set up MongoDB URI from environment or use a default URI
    app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

    # Initialize PyMongo with the app
    mongo.init_app(app)

    return app
