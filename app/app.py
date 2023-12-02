from flask import Flask, request, jsonify
from flask_cors import CORS
import requests 
import json
import time
from datetime import datetime
import bcrypt
from pymongo import MongoClient
import certifi

from algoliasearch.search_client import SearchClient
#python -m pip install --upgrade algoliasearch

app = Flask(__name__)
CORS(app)

#Server side code for setInterval in sending search analytics
ALGOLIA_APP_ID = 'QGXKTHTJGY'
ADMIN_API_KEY = '1819bc16cbfa59f046d7e9bc1260048a'
newterms_index = 'searchAnalytics'
search_index = 'searchterms'

search_client = SearchClient.create(ALGOLIA_APP_ID, ADMIN_API_KEY)
main_index = search_client.init_index(search_index)
analytics_index = search_client.init_index(newterms_index)

@app.route('/addPopularTerms', methods=['POST'])
def add_popular_terms():
    try:
        terms = request.json.get('terms', [])
        count_ = request.json.get('count', [])
        
        #required no. of searches in order to add to index
        add_threshold = 10
        
        termFound = False

        # Format the data for indexing in the main search index
        for index, term in enumerate(terms):
            if(len(term) <= 20):
                try:
                    get_count = analytics_index.get_object(f'term_{term}')
                    search_count = get_count['count']
                    termFound = True
                except Exception as e:
                    termFound = False
                    
                if(termFound == True):
                    if(search_count >= add_threshold) :
                        record = [{"objectID": f'term_{term}', "search_term": term, "source": "dealdetector"}]
                        main_index.save_objects(record)
                    else:
                        analytics_index.partial_update_object({
                            'count': { '_operation': 'Increment', 'value': 1 },
                            'objectID': f'term_{term}'
                        })
                else:
                    record = [{"objectID": f'term_{term}', "search_term": term, "count": count_[index]}]
                    analytics_index.save_objects(record)
                
        return jsonify({'success': True, "Terms": terms})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": "term already added or could not be added"}), 500
    
@app.after_request
def set_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Adjust the origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
#end of analytics code

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

token = 'OCNXKSNMBFLRRLWZWANKMIOLWSVWEAUYBCHWCADJLMYTVBAVKKNJGPFNZLUDXTVG'

@app.route('/search', methods=['POST'])
def search():
    global job_id
    search_query = request.json.get('searchQuery', '')
    data = {
        'token': token,
        'country': 'us',
        'source': 'google_shopping',
        'topic': 'product_and_offers',
        'key': 'term',
        'max_age': '1200',
        'max_pages': '1',
        # 'sort_by': 'price_ascending',
        'condition': 'any',
        'shipping': 'any',
        'values': search_query
    }

    post_response = requests.post('https://api.priceapi.com/v2/jobs', data=data)   
    job_id = post_response.json()['job_id']
    return job_id

@app.route('/results', methods=['GET'])
def results():
    global job_id
    time_alloted, max_time = 0, 20
    while time_alloted < max_time:
        response = requests.get(f'https://api.priceapi.com/v2/jobs/{job_id}/download?token={token}')

        if response.status_code == 200:
            try:
                json_data = json.loads(response.text)
                offers = json_data['results'][0]['content']['offers']
                if not offers:
                    return jsonify({'error': 'No offers found'}), 404

                cheapest_offer = min(offers, key = lambda x: float(x['price']))
                product_info = json_data['results'][0]['content']

                cheapest_product = {
                    'name': product_info['name'],
                    'description': product_info['description'],
                    'image_url': product_info['image_url'],
                    'price': cheapest_offer['price'],
                    'price_with_shipping': cheapest_offer['price_with_shipping'],
                }

                offer_info = [[offer['url'], offer['price']] for offer in offers]

                result_data = {
                    'cheapest_product': cheapest_product,
                    'offers': offer_info
                }

                print(f'Time needed: {time_alloted}s')
                return jsonify(result_data)
            except json.JSONDecodeError as e:
                return jsonify({'error': f'Failed to parse JSON: {str(e)}'}), 500
        elif time_alloted == max_time: 
            return jsonify({'error': 'Failed to retrieve data from Price API'}), response.status_code
        
        time.sleep(1)
        time_alloted += 1 

if __name__ == '__main__':
    app.run(debug=True)

