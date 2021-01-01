import datetime
import json
import re
from urllib.parse import quote_plus as encode_url

import mongoengine
from .exceptions import InvalidValue
from .utils import get_param_type


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

OPERATOR_TABLE = {
    "gt": "$gt",
    "lt": "$lt",
    "and": "$and",
}

def get_db_op(op):
    return OPERATOR_TABLE[op]

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

    def create_one_param_query(self, param, values):
        filters = []
        for value in values:
            try:
                op, value = value.split(":")
            except ValueError:
                raise InvalidValue
            param_type = get_param_type(param)
            filters.append({
                get_db_op(op): get_type_converter(param_type)(value)
            })

        return {param: filters}

    def create_query(self, query_dict):
        filters = []
        for param in query_dict.keys():
            values = query_dict.getlist(param)
            filters.append(self.create_one_param_query(param, values))

        return {get_db_op("and"): filters}
