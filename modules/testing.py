from pymongo import MongoClient

# Replace with your actual connection string
connection_string = 'mongodb+srv://mminalbe22:MINAL2302@cluster0.klqmf.mongodb.net/?retryWrites=true&w=majority'

try:
    client = MongoClient(connection_string)
    db = client['user_information']  # Replace with your actual database name
    print("Connected to MongoDB!")
except Exception as e:
    print("Could not connect to MongoDB:", e)