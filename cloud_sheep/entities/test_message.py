from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from .message import (
    TEXT_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    InvalidMessage,
    create_message,
    create_message_update,
)


class TooLongText(str):
    def __len__(self):
        return TEXT_MAX_LENGTH + 1


class TooLongTitle(str):
    def __len__(self):
        return TITLE_MAX_LENGTH + 1


@given(st.fixed_dictionaries({"text": st.text()}, optional={"title": st.text()}))
def test_create_message_with_valid_input(message):
    created_message = create_message(**message)

    assert created_message["text"] == message["text"]
    if "title" in message:
        assert created_message["title"] == message["title"]
    assert type(created_message["created_at"]) == datetime
    assert created_message["created_at"] == created_message["last_modified"]

    for key in ["text", "title", "created_at", "last_modified"]:
        if key in created_message:
            created_message.pop(key)
    assert len(created_message) == 0


@pytest.mark.parametrize(
    "message",
    [
        {},
        {"text": "text", "a": "a"},
        {"title": "title"},
        {"text": "text", "created_at": datetime.now()},
    ],
)
def test_create_message_with_wrong_params(message):
    with pytest.raises(InvalidMessage, match="Message is not valid."):
        create_message(**message)


@pytest.mark.parametrize(
    "message",
    [
        {"text": False},
        {"text": TooLongText()},
    ],
)
def test_create_message_with_invalid_text(message):
    with pytest.raises(InvalidMessage, match="Message's text is not valid."):
        create_message(**message)


@pytest.mark.parametrize(
    "message",
    [
        {"text": "text", "title": 5},
        {"text": "text", "title": TooLongTitle()},
    ],
)
def test_create_message_with_invalid_title(message):
    with pytest.raises(InvalidMessage, match="Message's title is not valid."):
        create_message(**message)


@given(st.dictionaries(st.sampled_from(["text", "title"]), st.text()))
def test_create_message_update_with_valid_input(message):
    created_message = create_message_update(**message)

    if "text" in message:
        assert created_message["text"] == message["text"]
    if "title" in message:
        assert created_message["title"] == message["title"]
    assert type(created_message["last_modified"]) == datetime

    for key in ["text", "title", "last_modified"]:
        if key in created_message:
            created_message.pop(key)
    assert len(created_message) == 0


@pytest.mark.parametrize(
    "message",
    [
        {"text": "text", "a": "a"},
        {"text": "text", "created_at": datetime.now()},
    ],
)
def test_create_message_update_with_wrong_params(message):
    with pytest.raises(InvalidMessage, match="Message is not valid."):
        create_message_update(**message)


@pytest.mark.parametrize(
    "message",
    [
        {"text": False},
        {"text": TooLongText()},
    ],
)
def test_create_message_update_with_invalid_text(message):
    with pytest.raises(InvalidMessage, match="Message's text is not valid."):
        create_message_update(**message)


@pytest.mark.parametrize(
    "message",
    [
        {"title": 5},
        {"text": "text", "title": TooLongTitle()},
    ],
)
def test_create_message_update_with_invalid_title(message):
    with pytest.raises(InvalidMessage, match="Message's title is not valid."):
        create_message_update(**message)
