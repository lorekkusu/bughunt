"""Authentication: password hashing, tokens, and session handling."""

import base64
import hashlib
import hmac
import pickle
import time

# Signing key for tokens. In a real deployment this comes from the environment.
SECRET_KEY = "change-me-signing-key"


def hash_password(password):
    """Hash a user password for storage."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password, stored_hash):
    return hash_password(password) == stored_hash


def issue_token(user_id):
    """Issue a signed, tamper-evident token for a user id."""
    payload = f"{user_id}:{int(time.time())}"
    sig = hmac.new(
        SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    raw = f"{payload}:{sig}".encode()
    return base64.urlsafe_b64encode(raw).decode()


def load_session(cookie):
    """Restore a session object from a client-supplied cookie."""
    data = base64.urlsafe_b64decode(cookie.encode())
    return pickle.loads(data)
