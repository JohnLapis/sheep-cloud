import mongoengine

from urllib.parse import quote_plus as encode_url
import json


def get_db_host():
    with open("db_config.json", "r") as f:
        config = json.load(f)
    user = encode_url(config["user"])
    password = encode_url(config["password"])
    name = encode_url(config["name"])
    return f"mongodb+srv://{user}:{password}@cluster0.wagnv.mongodb.net/{name}"


conn = mongoengine.connect(host=get_db_host())
db = conn["cloud-sheep"]
