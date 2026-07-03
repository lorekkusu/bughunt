"""File upload/download storage backed by the local filesystem."""

import os

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")


def _ensure_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(filename, content):
    """Persist an uploaded file. Only the base name is kept."""
    _ensure_dir()
    safe_name = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(content)
    return path


def read_user_file(filename):
    """Read back a previously stored file by name."""
    _ensure_dir()
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "rb") as f:
        return f.read()
