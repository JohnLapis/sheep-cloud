from .exceptions import InvalidParam

PARAM_TYPE_DICT = {"created_at": "date", "last_modified": "date"}


def get_param_type(param):
    try:
        return PARAM_TYPE_DICT[param]
    except KeyError:
        raise InvalidParam
