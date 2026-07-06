from pathlib import Path

from taskqueue.core.config import Config, load
from taskqueue.core.errors import ConfigError

import pytest

EXAMPLE = Path(__file__).resolve().parent.parent / "config.example.yaml"


def test_defaults():
    config = Config()
    assert config.max_attempts == 5
    assert config.plugin_modules() == []


def test_load_example_config():
    config = load(EXAMPLE)
    assert config.queue_max_size == 10_000
    assert config.workers == 4
    assert config.plugin_modules() == [
        "taskqueue.clients.plugins.audit",
        "taskqueue.clients.plugins.metrics_hook",
    ]


def test_unknown_key_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("no_such_key: 1\n")
    with pytest.raises(ConfigError):
        load(bad)


def test_bad_value_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("workers: many\n")
    with pytest.raises(ConfigError):
        load(bad)
