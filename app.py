import requests
from flask import Flask, request, jsonify
import json
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello, World'

@app.route('/get_price_data', methods=['GET', 'POST'])
def get_price_data():
    token = 'OCNXKSNMBFLRRLWZWANKMIOLWSVWEAUYBCHWCADJLMYTVBAVKKNJGPFNZLUDXTVG'
    data = {
        'token': token,
        'country': 'us',
        'source': 'google_shopping',
        'topic': 'product_and_offers',
        'key': 'term',
        'max_age': '1200',
        'max_pages': '1',
        'sort_by': 'ranking_descending',
        'condition': 'any',
        'shipping': 'any',
        'values': 'Black jeans'
    }

    post_response = requests.post('https://api.priceapi.com/v2/jobs', data=data)   
    job_id = post_response.json()['job_id']


    time.sleep(5)


    response = requests.get(f'https://api.priceapi.com/v2/jobs/{job_id}/download?token={token}')

    if response.status_code == 200:
        try:
            json_data = json.loads(response.text)
            return jsonify(json_data)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Failed to parse JSON: {str(e)}'}), 500

    return jsonify({'error': 'Failed to retrieve data from Price API'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
