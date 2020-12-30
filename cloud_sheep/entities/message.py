from datetime import datetime, timezone

TEXT_MAX_LENGTH = 50_000
TITLE_MAX_LENGTH = 50


def now():
    return datetime.now(timezone.utc)


def create_message(*, text, title=None):
    message = {}
    if title is not None:
        assert isinstance(title, str)
        assert len(title) <= TITLE_MAX_LENGTH
        message["title"] = title

    assert isinstance(text, str)
    assert len(text) <= TEXT_MAX_LENGTH
    message["text"] = text
    message["size"] = len(text)
    message["created_at"] = now()
    message["last_modified"] = now()
    return message


def validate_message(*, text=None, title=None):
    try:
        assert isinstance(text, str)
        assert len(text) <= TEXT_MAX_LENGTH
        assert isinstance(title, str)
        assert len(title) <= TITLE_MAX_LENGTH
        return True
    except Exception:
        return False
