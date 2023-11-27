from flask import Flask, request, jsonify
from flask_cors import CORS
import requests 
import json
import time
from datetime import datetime
import bcrypt
from pymongo import MongoClient
import certifi

app = Flask(__name__)
CORS(app)


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

@app.route('/get_price_data', methods=['GET', 'POST'])
def get_price_data():
    token = 'OCNXKSNMBFLRRLWZWANKMIOLWSVWEAUYBCHWCADJLMYTVBAVKKNJGPFNZLUDXTVG'
    search_query = request.json.get('searchQuery', '')
    data = {
        'token': 'OCNXKSNMBFLRRLWZWANKMIOLWSVWEAUYBCHWCADJLMYTVBAVKKNJGPFNZLUDXTVG',
        'country': 'us',
        'source': 'google_shopping',
        'topic': 'product_and_offers',
        'key': 'term',
        'max_age': '1200',
        'max_pages': '1',
        'condition': 'any',
        'shipping': 'any',
        'values': search_query, 
    }


    post_response = requests.post('https://api.priceapi.com/v2/jobs', data=data)   
    job_id = post_response.json()['job_id']

    time_alloted, max_time = 0, 60
    while time_alloted < max_time:
        response = requests.get(f'https://api.priceapi.com/v2/jobs/{job_id}/download?token={token}')

        if response.status_code == 200:
            try:
                json_data = json.loads(response.text)
                print(f'Time needed: {time_alloted}s')
                return jsonify(json_data)
            except json.JSONDecodeError as e:
                return jsonify({'error': f'Failed to parse JSON: {str(e)}'}), 500
        elif time_alloted == max_time: 
            return jsonify({'error': 'Failed to retrieve data from Price API'}), response.status_code
        
        time.sleep(2)
        time_alloted += 2 

if __name__ == '__main__':
    app.run(debug=True)

