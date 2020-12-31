from datetime import datetime

import pytest

from .utils import InvalidDate, convert_to_date


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
    with pytest.raises(InvalidDate):
        assert convert_to_date(date)
