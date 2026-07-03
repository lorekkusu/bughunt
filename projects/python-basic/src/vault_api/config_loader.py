"""YAML configuration loading."""

import yaml

DEFAULTS = {
    "max_upload_mb": 10,
    "session_ttl": 3600,
}


def load_config(path):
    """Load configuration from a YAML file, falling back to defaults."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except Exception:
        data = None

    merged = dict(DEFAULTS)
    if data:
        merged.update(data)
    return merged
