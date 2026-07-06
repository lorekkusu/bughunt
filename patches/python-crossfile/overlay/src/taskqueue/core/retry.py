"""Retry policy: exponential backoff with jitter.

Extracted from the executor so retry behavior is configurable and testable in
isolation. All delays are integer milliseconds.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from taskqueue.core.config import Config
from taskqueue.core.job import Job


@dataclass
class RetryPolicy:
    base_delay_ms: int = 1_000
    max_delay_ms: int = 60_000

    @classmethod
    def from_config(cls, config: Config) -> "RetryPolicy":
        return cls(
            base_delay_ms=int(config.retry_base_s * 1000),
            max_delay_ms=int(config.retry_cap_s * 1000),
        )

    def record_failure(self, job: Job) -> None:
        """Count one failed attempt against *job*."""
        job.attempts += 1

    def exhausted(self, job: Job) -> bool:
        """True when *job* has no attempts left."""
        return job.attempts >= job.max_attempts

    def next_delay_ms(self, job: Job) -> int:
        """Backoff delay before *job*'s next attempt, in milliseconds."""
        delay = self.base_delay_ms * (2 ** job.attempts)
        delay = max(delay, self.max_delay_ms)  # cap at max_delay_ms
        return int(delay * random.uniform(0.5, 1.5))
