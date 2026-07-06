"""Schema migrations for persisted job payload dicts.

Snapshots written by older releases carry an older ``schema_version``;
:func:`upgrade` brings a record up to :data:`SCHEMA_VERSION` by applying each
step migration in order. Records with no ``schema_version`` key are treated
as version 1 (the field was introduced in version 2).

Every migration takes a dict and returns a dict; :func:`upgrade` never
mutates its input and is a no-op (beyond copying) for already-current
records.
"""

from __future__ import annotations

from typing import Any, Callable

#: The schema version this release reads and writes.
SCHEMA_VERSION = 3


def _v1_to_v2(record: dict[str, Any]) -> dict[str, Any]:
    """v2 renamed the ``prio`` field to ``priority`` (default ``"normal"``)."""
    upgraded = dict(record)
    if "prio" in upgraded:
        upgraded["priority"] = upgraded.pop("prio")
    else:
        upgraded.setdefault("priority", "normal")
    return upgraded


def _v2_to_v3(record: dict[str, Any]) -> dict[str, Any]:
    """v3 made ``tags`` a required list field."""
    upgraded = dict(record)
    if not isinstance(upgraded.get("tags"), list):
        upgraded["tags"] = []
    return upgraded


#: Step migrations, keyed by the version they upgrade *from*.
CURRENT: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {
    1: _v1_to_v2,
    2: _v2_to_v3,
}


def upgrade(record: dict[str, Any]) -> dict[str, Any]:
    """Return a new dict upgraded to :data:`SCHEMA_VERSION`.

    The input is never mutated. Records already at the current version are
    returned as a stamped copy unchanged otherwise, so the function is
    idempotent: ``upgrade(upgrade(r)) == upgrade(r)``.
    """
    upgraded = dict(record)
    version = int(upgraded.get("schema_version", 1))
    while version < SCHEMA_VERSION:
        step = CURRENT.get(version)
        if step is None:
            raise ValueError(f"cannot upgrade from unknown schema version {version}")
        upgraded = step(upgraded)
        version += 1
    upgraded["schema_version"] = SCHEMA_VERSION
    return upgraded
