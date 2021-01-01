import datetime
import json
import re
from urllib.parse import quote_plus as encode_url

import mongoengine
from .exceptions import InvalidValue


def convert_to_date(value):
    try:
        PATTERN = re.compile(r"^(?P<year>\d{4})(?P<month>\d{2})?(?P<day>\d{2})?$")
        match = re.match(PATTERN, value).groupdict(default=0)
        match["year"] = int(match["year"])
        match["month"] = int(match["month"]) or 1
        match["day"] = int(match["day"]) or 1
        return datetime.datetime(**match)
    except (AttributeError, TypeError):
        raise InvalidValue


TYPE_CONVERTER_DICT = {
    "date": convert_to_date,
}


def get_type_converter(type):
    return TYPE_CONVERTER_DICT[type]


def get_db_host():
    with open("db_config.json", "r") as f:
        config = json.load(f)
        user = encode_url(config["user"])
        password = encode_url(config["password"])
        name = encode_url(config["name"])
    return f"mongodb+srv://{user}:{password}@cluster0.wagnv.mongodb.net/{name}"


class DatabaseClient:
    def __init__(self):
        self.conn = mongoengine.connect(host=get_db_host())
        self._db = self.conn["cloud-sheep"]

    def __getattr__(self, name):
        return getattr(self._db, name)
