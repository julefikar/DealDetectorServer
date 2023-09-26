import certifi
from flask import Flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

app.config.from_pyfile('../dev.env')

def get_mongo_client():
    uri = app.config['MONGODB_URI']
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    return client

@app.route('/')
def hello_world():
    client = get_mongo_client()
    try:
        client.admin.command('ping')
        return "Pinged your deployment. You successfully connected to MongoDB!"
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run()