import datetime
import json
import re
from urllib.parse import quote_plus as encode_url

import mongoengine
import pymongo

from .entities.param import get_param_type, parse_param_expr


class InvalidQuery(Exception):
    pass


class InvalidValue(Exception):
    pass


class InvalidOperator(Exception):
    pass


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
    "text": str,
}


def get_type_converter(param):
    return TYPE_CONVERTER_DICT[get_param_type(param)]


OPERATOR_TABLE = {
    "gt": "$gt",
    "lt": "$lt",
    "and": "$and",
    "text": "$text",
    "rg": "$regex",
    "op": "$options",
    "search": "$search",
    "language": "$language",
    "case_sensitivity": "$caseSensitive",
    "diacritic_sensitivity": "$diacriticSensitive",
    "set": "$set",
}


def get_db_op(op):
    try:
        return OPERATOR_TABLE[op]
    except KeyError:
        raise InvalidOperator(f"{op} operator doesn't exist.")


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

    def create_param_query(self, param, exprs):
        operations = {}
        for expr in exprs:
            op, value = parse_param_expr(param, expr)
            operations[get_db_op(op)] = get_type_converter(param)(value)

        return {param: operations}

    def create_query(self, query_dict):
        subqueries = []
        if "q" in query_dict:
            subqueries.append(self.create_text_query(query_dict))

        for param in query_dict.keys():
            values = query_dict.getlist(param)
            subqueries.append(self.create_param_query(param, values))

        if not subqueries:
            raise InvalidQuery("No parameters were given.")

        return {get_db_op("and"): subqueries}

    def create_text_query(self, query_dict):
        flags, text = parse_param_expr("q", query_dict.pop("q"))
        return {
            get_db_op("text"): {
                get_db_op("search"): text,
                get_db_op("language"): query_dict.pop("lang", default="none"),
                get_db_op("case_sensitivity"): "c" in flags,
                get_db_op("diacritic_sensitivity"): "d" in flags,
            }
        }

    def create_update_query(self, update):
        try:
            return {get_db_op("set"): {**update}}
        except TypeError:
            raise InvalidValue('"update" value is not a dictionary.')

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
