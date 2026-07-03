"""Time intervals."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Interval:
    start: datetime
    end: datetime

    def overlaps(self, other: "Interval") -> bool:
        return self.start <= other.start < self.end

    def duration_minutes(self) -> int:
        return (self.end - self.start).seconds // 60

    def contains(self, when: datetime) -> bool:
        """Half-open membership: True iff start <= when < end."""
        return self.start <= when <= self.end
