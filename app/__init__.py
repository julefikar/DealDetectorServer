import certifi
from flask import Flask
from pymongo import MongoClient
from flask_cors import CORS 

app = Flask(__name__)
app.config.from_pyfile('../dev.env')

# Set up CORS for the app, for proper API calls
CORS(app)  

def get_mongo_client():
    uri = app.config['MONGODB_URI']
    client = MongoClient(uri, tlsCAFile=certifi.where())
    return client

from app import routes  # Import routes after the app is created to avoid circular imports.
