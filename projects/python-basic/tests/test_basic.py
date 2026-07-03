from vault_api import auth, tasks, utils


def test_token_roundtrip_shape():
    token = auth.issue_token(1)
    assert isinstance(token, str)
    assert len(token) > 10


def test_paginate_returns_list():
    result = utils.paginate(list(range(100)), 0)
    assert isinstance(result, list)


def test_is_active_true():
    assert utils.is_active("active") is True


def test_parse_task_spec():
    assert tasks.parse_task_spec("{'retries': 3}") == {"retries": 3}


def test_password_verify_roundtrip():
    h = auth.hash_password("hunter2")
    assert auth.verify_password("hunter2", h)
