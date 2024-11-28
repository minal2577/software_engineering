from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os
from modules.auth import auth_bp
from modules.shipping import address_bp
from modules.search import products_bp
from modules.cart import cart_bp
from modules.payment import payment_bp
load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "593574a5feb45952facd62c76dfb478a65bfdfe1b9121b8f0210b661a0a0289e")

mongo = PyMongo(app)
jwt = JWTManager(app)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(address_bp, url_prefix='/shipping') 
app.register_blueprint(products_bp, url_prefix='/products') 
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(payment_bp, url_prefix='/payment_process')
@app.route('/')
def home():
    return "MongoDB connected successfully!"
    @app.route('/')
def serve_homepage():
    return render_template('index.html')
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('new', filename)
if __name__ == '__main__':
    app.run(debug=True)
