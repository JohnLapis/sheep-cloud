class InvalidExpression(Exception):
    pass


class InvalidParam(Exception):
    pass


class Param:
    def __init__(self, type):
        self.type = type


class DateParam(Param):
    def __init__(self):
        super().__init__("date")

    def parse(self, expr):
        return expr.split(":")


class TextParam(Param):
    def __init__(self):
        super().__init__("text")

    def parse(self, expr):
        return expr.split(":")


class TextSearchParam(Param):
    def __init__(self):
        super().__init__("text")

    def parse(self, expr):
        if ":" in expr:
            return expr.split(":")
        else:
            return "", expr


PARAM_DICT = {
    "created_at": DateParam(),
    "last_modified": DateParam(),
    "title": TextParam(),
    "text": TextParam(),
    "q": TextSearchParam(),
}


def get_param(name):
    try:
        return PARAM_DICT[name]
    except KeyError:
        raise InvalidParam(f"{name} is not a valid parameter.")


def get_param_type(param_name):
    return get_param(param_name).type


def get_param_parser(param_name):
    return get_param(param_name).parse


def parse_param_expr(param, expr):
    try:
        op, value = get_param_parser(param)(expr)
        return op, value
    except ValueError:
        raise InvalidExpression(f"{expr} is not a valid expression.")
