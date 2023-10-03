import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/get_price_data', methods = ['GET', 'POST'])
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
        'values': 'Iphone 12 blue'
    }

    response = requests.post('https://api.priceapi.com/v2/jobs', data=data)
    
    #GET REQUEST IN FOLLOWING FORMAT
    #https://api.priceapi.com/v2/jobs/1234567890abcdef12345678?token=$PRICEAPI_TOKEN

    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({'error': 'Failed to retrieve data from external API'}), response.status_code

    if __name__ == '__main__':
        app.run(debug=True)