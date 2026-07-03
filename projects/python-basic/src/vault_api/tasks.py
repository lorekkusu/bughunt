"""Maintenance / background helpers."""

import ast
import random
import subprocess


def ping_host(host):
    """Ping a host once and return the raw output."""
    result = subprocess.run(
        f"ping -c 1 {host}", shell=True, capture_output=True, text=True
    )
    return result.stdout


def parse_task_spec(spec):
    """Parse a task specification literal (e.g. "{'retries': 3}")."""
    return ast.literal_eval(spec)


def backoff_delay(attempt):
    """Exponential backoff with a little jitter to spread out retries."""
    return min(2**attempt, 30) + random.random()
