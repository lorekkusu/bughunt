"""Operator command-line interface.

Every command builds a full in-process service (:class:`taskqueue.api.app.App`)
from the config file and talks to it through the in-memory transport — the
same code path as a networked deployment, minus the socket. ``snapshot`` and
``restore`` operate on the app's store via :mod:`taskqueue.storage.backup`.

Exit codes: 0 on success, 1 for service-level errors (unknown job, invalid
submission, missing snapshot file), 2 for bad command-line arguments.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Optional, Sequence

from taskqueue.core.errors import TaskQueueError
from taskqueue.core.priority import DEFAULT_PRIORITY, PRIORITIES

log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taskqueue", description="taskqueue operator CLI")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="path to the config file")
    sub = parser.add_subparsers(dest="command", required=True)

    submit = sub.add_parser("submit", help="submit a job")
    submit.add_argument("name", help="job name (routes to a handler)")
    submit.add_argument("--priority", default=DEFAULT_PRIORITY, choices=PRIORITIES)
    submit.add_argument("--payload", default="{}", help="job payload as a JSON object")

    status = sub.add_parser("status", help="show a job's current status")
    status.add_argument("job_id")

    timeline = sub.add_parser("timeline", help="show a job's lifecycle events")
    timeline.add_argument("job_id")

    snapshot = sub.add_parser("snapshot", help="export the job store to a file")
    snapshot.add_argument("path")

    restore = sub.add_parser("restore", help="load a snapshot file into the store")
    restore.add_argument("path")

    return parser


def _load_config(path: str):
    from taskqueue.core.config import Config, load

    try:
        return load(path)
    except FileNotFoundError:
        log.info("config file %s not found; using defaults", path)
        return Config()


def main(argv: Optional[Sequence[str]] = None) -> int:
    # Imported lazily to keep this module importable on its own and to avoid
    # import cycles with the api package.
    from taskqueue.api.app import App
    from taskqueue.clients.http import InMemoryTransport
    from taskqueue.clients.sdk import Client
    from taskqueue.storage import backup

    args = build_parser().parse_args(argv)

    if args.command == "submit":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as exc:
            print(f"invalid --payload JSON: {exc}", file=sys.stderr)
            return 2
        if not isinstance(payload, dict):
            print("--payload must be a JSON object", file=sys.stderr)
            return 2
    else:
        payload = None

    config = _load_config(args.config)
    app = App(config)
    client = Client(InMemoryTransport(app), events_path=config.events_path)

    try:
        if args.command == "submit":
            job_id = client.submit(args.name, payload=payload, priority=args.priority)
            print(json.dumps({"id": job_id}))
        elif args.command == "status":
            print(json.dumps(client.status(args.job_id)))
        elif args.command == "timeline":
            entries = [
                {
                    "kind": entry.kind,
                    "at": entry.at.isoformat(),
                    "since_previous_s": entry.since_previous_s,
                }
                for entry in client.job_timeline(args.job_id)
            ]
            print(json.dumps(entries))
        elif args.command == "snapshot":
            count = backup.export_snapshot(app.store, args.path)
            print(json.dumps({"snapshot": args.path, "jobs": count}))
        else:  # restore — argparse guarantees the command is one of the five
            count = backup.restore_into(app.store, args.path)
            print(json.dumps({"restored": args.path, "jobs": count}))
    except (TaskQueueError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
