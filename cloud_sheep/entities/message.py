from datetime import datetime, timezone

TEXT_MAX_LENGTH = 50_000
TITLE_MAX_LENGTH = 50


class InvalidMessage(Exception):
    pass


def now():
    return datetime.now(timezone.utc)


def create_message(*, text=None, title=None, **kwargs):
    try:
        assert text is not None and not kwargs
        message = {}
        if title is not None:
            validate_title(title)
            message["title"] = title

        validate_text(text)
        message["text"] = text
        message["created_at"] = now()
        message["last_modified"] = message["created_at"]
        return message
    except AssertionError:
        raise InvalidMessage("Message is not valid.")


def validate_text(text):
    try:
        assert isinstance(text, str)
        assert len(text) <= TEXT_MAX_LENGTH
    except AssertionError:
        raise InvalidMessage("Message's text is not valid.")


def validate_title(title):
    try:
        assert isinstance(title, str)
        assert len(title) <= TITLE_MAX_LENGTH
    except AssertionError:
        raise InvalidMessage("Message's title is not valid.")
