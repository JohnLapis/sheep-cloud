from urllib.parse import quote_plus as encode_url
import json

from flask import Flask, Blueprint
import mongoengine

from .message import Message


LATEST_VERSION = 'v1'

app = Flask(__name__)

def get_db_host():
    with open("db_config.json", "r") as f:
        config = json.load(f)
    user = encode_url(config['user'])
    password = encode_url(config['password'])
    name = encode_url(config['name'])
    return f'mongodb+srv://{user}:{password}@cluster0.wagnv.mongodb.net/{name}'

db = mongoengine.connect(host=get_db_host())['cloud-sheep']

api_bp = Blueprint('api', __name__)
api_bp.add_url_rule(
    '/message/<int:id>',
    view_func=Message.as_view('message', db['message']))

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(api_bp, url_prefix=f'/api/{LATEST_VERSION}')
