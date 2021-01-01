import datetime
import json
import re
from urllib.parse import quote_plus as encode_url

import mongoengine
import pymongo

from .exceptions import InvalidQuery, InvalidValue
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
        raise InvalidValue(f"{value} is not a valid date.")


TYPE_CONVERTER_DICT = {
    "date": convert_to_date,
}


def get_type_converter(param):
    return TYPE_CONVERTER_DICT[get_param_type(param)]


OPERATOR_TABLE = {
    "gt": "$gt",
    "lt": "$lt",
    "and": "$and",
}


def get_db_op(op):
    try:
        return OPERATOR_TABLE[op]
    except KeyError:
        raise InvalidValue(f"{op} operator doesn't exist.")


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

    def create_one_param_query(self, param, exprs):
        query_exprs = {}
        for expr in exprs:
            try:
                op, value = expr.split(":")
            except ValueError:
                raise InvalidValue(f"{expr} is not a valid value.")
            query_exprs[get_db_op(op)] = get_type_converter(param)(value)

        return {param: query_exprs}

    def create_query(self, query_dict):
        filters = []
        for param in query_dict.keys():
            values = query_dict.getlist(param)
            filters.append(self.create_one_param_query(param, values))

        if not filters:
            raise InvalidQuery("No parameters were given.")

        return {get_db_op("and"): filters}

    def get_sort_param(self, param):
        try:
            if param[0] == "-":
                param = param[1:]
                direction = pymongo.DESCENDING
            else:
                direction = pymongo.ASCENDING

            assert len(param) > 0
            return (param, direction)
        except (IndexError, AssertionError):
            raise InvalidValue("The limit parameter should be a positive integer.")

    def get_limit_param(self, param):
        try:
            return 0 if param is None else int(param)
        except ValueError:
            raise InvalidValue("The limit parameter should be a positive integer.")
