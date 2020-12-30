from datetime import datetime

import pytest
from .message import create_message


def test_instantiation_with_title():
    params = {"title": "test title", "text": "test text"}
    message = create_message(**params)

    assert message["text"] == params["text"]
    assert message["size"] == len(params["text"])
    assert message["title"] == params["title"]
    assert isinstance(message["last_modified"], datetime)
    assert isinstance(message["created_at"], datetime)


def test_instantiation_without_title():
    params = {"text": "test text"}
    message = create_message(**params)

    assert message["text"] == params["text"]
    assert message["size"] == len(params["text"])
    with pytest.raises(KeyError):
        message["title"]
    assert isinstance(message["last_modified"], datetime)
    assert isinstance(message["created_at"], datetime)


def test_instantiation_with_text_larger_than_max():
    class MockText(str):
        def __len__(self):
            return 100_000

    with pytest.raises(AssertionError):
        create_message(text=MockText())


def test_instantiation_with_title_larger_than_max():
    class MockTitle(str):
        def __len__(self):
            return 100_000

    with pytest.raises(AssertionError):
        create_message(text="", title=MockTitle())
