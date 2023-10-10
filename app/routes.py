from app import app, get_mongo_client
from datetime import datetime
from flask import request, jsonify
import bcrypt

@app.route('/')
def hello_world():
    client = get_mongo_client()
    try:
        client.admin.command('ping')
        return "Pinged your deployment. You successfully connected to MongoDB!"
    except Exception as e:
        return str(e)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    client = get_mongo_client()
    db = client['DealDetector']
    users_collection = db['users']

    # Check if user already exists
    existing_user = users_collection.find_one({'username': data['username']})
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    # Hash the password
    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    user = {
        "username": data['username'],
        "password": hashed_pw,
        "email": data['email'],
        "created_at": datetime.now()
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully!"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    client = get_mongo_client()
    db = client['DealDetector'] 
    users_collection = db['users']

    user = users_collection.find_one({'username': data['username']})
    if not user:
        return jsonify({"error": "Username not found"}), 400

    # Verify password
    if bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"error": "Invalid password"}), 400
