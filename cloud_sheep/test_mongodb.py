from datetime import datetime

import pymongo
import pytest
from werkzeug.datastructures import MultiDict

from .entities.param import InvalidExpression, InvalidParam
from .mongodb import DatabaseClient, InvalidQuery, InvalidValue, convert_to_date


@pytest.fixture
def app(scope="module"):
    from flask import Flask

    return Flask(__name__)


class TestDatabaseClient:
    @classmethod
    def setup_class(cls):
        cls.client = DatabaseClient()

    @classmethod
    def teardown_class(cls):
        cls.client.conn.close()

    @pytest.mark.parametrize(
        "param,exprs,expected",
        [
            (
                "created_at",
                ["lt:2020"],
                {"created_at": {"$lt": datetime(year=2020, month=1, day=1)}},
            ),
            (
                "last_modified",
                ["gt:202012"],
                {"last_modified": {"$gt": datetime(year=2020, month=12, day=1)}},
            ),
            (
                "created_at",
                ["lt:20201230", "gt:20201229"],
                {
                    "created_at": {
                        "$lt": datetime(year=2020, month=12, day=30),
                        "$gt": datetime(year=2020, month=12, day=29),
                    },
                },
            ),
            (
                "title",
                ["rg:some regular expression", "op:ims"],
                {
                    "title": {
                        "$regex": "some regular expression",
                        "$options": "ims",
                    },
                },
            ),
        ],
    )
    def test_create_generic_query_with_valid_input(self, param, exprs, expected):
        assert self.client.create_generic_query(param, exprs) == expected

    @pytest.mark.parametrize(
        "param,exprs,error",
        [
            ("created_at", ["lt:not a date"], InvalidValue),
            ("invalid param", ["xx:whatever"], InvalidParam),
            ("last_modified", ["xx:whatever"], InvalidValue),
            ("created_at", [""], InvalidExpression),
        ],
    )
    def test_create_generic_query_with_invalid_input(self, param, exprs, error):
        with pytest.raises(error):
            self.client.create_generic_query(param, exprs)

    @pytest.mark.parametrize(
        "url_query,expected",
        [
            (
                "/api/messages?created_at=lt:2020",
                {
                    "$and": [
                        {"created_at": {"$lt": datetime(year=2020, month=1, day=1)}}
                    ]
                },
            ),
            (
                "/api/messages?last_modified=gt:202011",
                {
                    "$and": [
                        {
                            "last_modified": {
                                "$gt": datetime(year=2020, month=11, day=1)
                            }
                        }
                    ]
                },
            ),
            (
                "/api/messages?created_at=gt:20200625&created_at=lt:202011"
                + "&last_modified=gt:202012",
                {
                    "$and": [
                        {
                            "created_at": {
                                "$gt": datetime(year=2020, month=6, day=25),
                                "$lt": datetime(year=2020, month=11, day=1),
                            },
                        },
                        {
                            "last_modified": {
                                "$gt": datetime(year=2020, month=12, day=1)
                            },
                        },
                    ],
                },
            ),
            (
                "/api/message?q=c:some text search&lang=en&created_at=gt:20210101",
                {
                    "$and": [
                        {
                            "$text": {
                                "$search": "some text search",
                                "$language": "en",
                                "$caseSensitive": True,
                                "$diacriticSensitive": False,
                            },
                        },
                        {
                            "created_at": {
                                "$gt": datetime(year=2021, month=1, day=1)
                            },
                        },
                    ],
                },
            ),
        ],
    )
    def test_create_query_with_valid_input(self, app, url_query, expected):
        with app.test_request_context(url_query) as ctx:
            assert self.client.create_query(MultiDict(ctx.request.args)) == expected

    @pytest.mark.parametrize(
        "url_query,error",
        [
            ("/api/messages", InvalidQuery),
            ("/api/messages?a=", InvalidParam),
            ("/api/messages?&=a==", InvalidParam),
            ("/api/messages?created_at=5", InvalidExpression),
        ],
    )
    def test_create_query_with_invalid_input(self, app, url_query, error):
        with app.test_request_context(url_query) as ctx:
            with pytest.raises(error):
                self.client.create_query(MultiDict(ctx.request.args))

    @pytest.mark.parametrize(
        "url_query,expected",
        [
            (
                "/api/message?q=c:some text search&lang=en",
                {
                    "$text": {
                        "$search": "some text search",
                        "$language": "en",
                        "$caseSensitive": True,
                        "$diacriticSensitive": False,
                    }
                },
            ),
            (
                "/api/message?q=d:some text search",
                {
                    "$text": {
                        "$search": "some text search",
                        "$language": "none",
                        "$caseSensitive": False,
                        "$diacriticSensitive": True,
                    }
                },
            ),
            (
                "/api/message?q=some text search",
                {
                    "$text": {
                        "$search": "some text search",
                        "$language": "none",
                        "$caseSensitive": False,
                        "$diacriticSensitive": False,
                    }
                },
            ),
        ],
    )
    def test_create_text_query_with_valid_input(self, app, url_query, expected):
        with app.test_request_context(url_query) as ctx:
            assert (
                self.client.create_text_query(MultiDict(ctx.request.args))
                == expected
            )

    @pytest.mark.skip
    def test_create_text_query_with_invalid_input(self, app, url_query, error):
        pass

    @pytest.mark.parametrize(
        "param,expected",
        [
            ("-param", ("param", pymongo.DESCENDING)),
            ("param", ("param", pymongo.ASCENDING)),
        ],
    )
    def test_get_sort_param_valid_params(self, param, expected):
        assert self.client.get_sort_param(param) == expected

    @pytest.mark.parametrize("param", ["-", ""])
    def test_get_sort_param_invalid_params(self, param):
        with pytest.raises(InvalidValue):
            self.client.get_sort_param(param)

    @pytest.mark.parametrize("param,expected", [("3", 3), (None, 0)])
    def test_get_limit_param_valid_params(self, param, expected):
        assert self.client.get_limit_param(param) == expected

    @pytest.mark.parametrize("param", ["", "a"])
    def test_get_limit_param_invalid_params(self, param):
        with pytest.raises(InvalidValue):
            self.client.get_limit_param(param)


@pytest.mark.parametrize(
    "date,expected",
    [
        ("20201203", datetime(year=2020, month=12, day=3)),
        ("202012", datetime(year=2020, month=12, day=1)),
        ("2020", datetime(year=2020, month=1, day=1)),
    ],
)
def test_convert_to_date_with_valid_input(date, expected):
    assert convert_to_date(date) == expected


@pytest.mark.parametrize(
    "date",
    [
        "2020121",
        "2020120",
        "20201",
        "202",
        "2020a",
        "a202",
        "202012011",
        "a202012",
    ],
)
def test_convert_to_date_with_invalid_input(date):
    with pytest.raises(InvalidValue):
        assert convert_to_date(date)
