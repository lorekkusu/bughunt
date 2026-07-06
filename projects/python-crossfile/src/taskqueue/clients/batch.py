"""Client-side bulk submission.

:class:`BatchSubmitter` takes an iterable of job specs, validates each one
locally, and submits the valid ones through the SDK client one at a time —
a transport failure for one spec never aborts the rest of the batch. The
result maps every input index to either a job id or an error message, so
callers can retry exactly the specs that did not make it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from taskqueue.clients.http import TransportError, TransportTimeout
from taskqueue.clients.sdk import Client

log = logging.getLogger(__name__)

#: Default number of specs per progress-log chunk.
DEFAULT_CHUNK_SIZE = 50


@dataclass
class BatchResult:
    """Outcome of one :meth:`BatchSubmitter.submit_many` call.

    ``submitted`` holds ``(input_index, job_id)`` pairs; ``failed`` holds
    ``(input_index, error_message)`` pairs covering both local validation
    rejections and transport failures. Indices refer to positions in the
    original ``specs`` iterable, and each list is sorted by index.
    """

    submitted: list[tuple[int, str]] = field(default_factory=list)
    failed: list[tuple[int, str]] = field(default_factory=list)

    def ok(self) -> bool:
        """True if every spec in the batch was submitted successfully."""
        return not self.failed


class BatchSubmitter:
    """Submits many job specs through a :class:`~taskqueue.clients.sdk.Client`.

    Chunking exists purely so long batches emit periodic progress log lines
    ("submitted chunk 2/4"); specs are still validated and submitted one by
    one, and the chunk boundary has no semantic effect on the result.
    """

    def __init__(self, client: Client, chunk_size: int = DEFAULT_CHUNK_SIZE):
        if chunk_size < 1:
            raise ValueError(f"chunk_size must be at least 1, got {chunk_size}")
        self._client = client
        self._chunk_size = chunk_size

    @staticmethod
    def _validate(spec: Any) -> Optional[str]:
        """Local sanity check for one spec; returns an error message or None."""
        if not isinstance(spec, dict):
            return "spec must be a dict"
        name = spec.get("name")
        if not isinstance(name, str) or not name.strip():
            return "'name' is required and must be a non-empty string"
        if "payload" in spec and not isinstance(spec["payload"], dict):
            return "'payload' must be a dict"
        if "priority" in spec and (
            not isinstance(spec["priority"], str) or not spec["priority"].strip()
        ):
            return "'priority' must be a non-empty string"
        return None

    def submit_many(self, specs: Iterable[dict]) -> BatchResult:
        """Validate and submit every spec, never aborting mid-batch.

        Invalid specs are rejected locally and never sent. Valid specs are
        submitted in input order; :class:`TransportError` and
        :class:`TransportTimeout` from an individual submission are captured
        as per-index failures and the batch continues. Any other exception
        is a programming error and propagates.
        """
        result = BatchResult()
        valid: list[tuple[int, dict]] = []
        for index, spec in enumerate(specs):
            error = self._validate(spec)
            if error is not None:
                result.failed.append((index, error))
            else:
                valid.append((index, spec))

        total_chunks = (len(valid) + self._chunk_size - 1) // self._chunk_size
        for chunk_number in range(1, total_chunks + 1):
            start = (chunk_number - 1) * self._chunk_size
            for index, spec in valid[start : start + self._chunk_size]:
                try:
                    job_id = self._client.submit(
                        spec["name"],
                        payload=spec.get("payload"),
                        priority=spec.get("priority", "normal"),
                    )
                except (TransportError, TransportTimeout) as exc:
                    result.failed.append((index, str(exc)))
                else:
                    result.submitted.append((index, job_id))
            log.info("submitted chunk %d/%d", chunk_number, total_chunks)

        # Validation failures were collected before transport failures, so
        # re-sort to present one coherent index order.
        result.failed.sort(key=lambda pair: pair[0])
        return result
