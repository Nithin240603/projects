# config/config.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

# URL encode the username and password
username = quote_plus('RagulaNithin')
password = quote_plus('7266388rN@123')

# Construct the URI with the URL-encoded username and password
uri = f"mongodb+srv://{username}:{password}@nithin.e2pemlk.mongodb.net/?retryWrites=true&w=majority&appName=NITHIN"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.Blogging

blogs_collection = db["blogs"]
comments_collection = db["comments"]
users_collection = db["users"]  # Ensure this collection is defined

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Error:", e)
