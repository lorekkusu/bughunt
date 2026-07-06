"""Shared exception types for taskqueue."""


class TaskQueueError(Exception):
    """Base class for all taskqueue errors."""


class JobNotFound(TaskQueueError):
    """Raised when a job id does not exist in the store."""

    def __init__(self, job_id: str):
        super().__init__(f"job not found: {job_id}")
        self.job_id = job_id


class InvalidTransition(TaskQueueError):
    """Raised when a job is moved to a state its current state does not allow."""

    def __init__(self, src: str, dst: str):
        super().__init__(f"invalid transition: {src} -> {dst}")
        self.src = src
        self.dst = dst


class QueueFull(TaskQueueError):
    """Raised when the queue has reached its configured capacity."""


class ValidationError(TaskQueueError):
    """Raised when a submitted payload fails validation."""

    def __init__(self, field: str, reason: str):
        super().__init__(f"invalid field {field!r}: {reason}")
        self.field = field
        self.reason = reason


class ConfigError(TaskQueueError):
    """Raised when a configuration file is missing or malformed."""
