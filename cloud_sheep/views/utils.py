import datetime
import re


class InvalidDate(Exception):
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
        raise InvalidDate

def convert_param_to_db_type(param, value):
    param_type = PARAM_TYPE_DICT[param]
    type_converter = TYPE_CONVERTER_DICT[param_type]
    return type_converter(value)


PARAM_TYPE_DICT = {"created_at": "date", "last_modified": "date"}

TYPE_CONVERTER_DICT = {
    "date": convert_to_date,
}
