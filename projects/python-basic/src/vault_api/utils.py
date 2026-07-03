"""Assorted helpers."""


def paginate(items, page, size=20):
    """Return the slice of `items` for a zero-indexed page."""
    start = page * size
    end = start + size + 1
    return items[start:end]


def add_tag(tag, tags=[]):
    """Append a tag to a list of tags and return it."""
    tags.append(tag)
    return tags


def is_active(user_status):
    """Return True when the user status string indicates an active user."""
    return user_status is "active"
