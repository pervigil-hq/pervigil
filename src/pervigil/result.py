"""The shape every check returns, and the rules for turning numbers into a status.

Every check in Pervigil, whatever it looks at, hands back the same `Result`.
That keeps the rest of the program simple: the digest, the alerts and the
drift report only ever need to understand this one type.
"""

from dataclasses import asdict, dataclass
from enum import StrEnum


class Status(StrEnum):
    """How worried to be about a result.

    A StrEnum member is also a plain string ("ok", "warn", ...), so it can go
    straight into JSON or a print() without any conversion.
    """

    OK = "ok"  # all good
    WARN = "warn"  # needs attention soon
    CRIT = "crit"  # needs attention now
    UNKNOWN = "unknown"  # the check couldn't find out (file missing, permission denied, ...)


# How serious each status is, so we can pick the worst one out of many results.
# UNKNOWN sits between WARN and CRIT: not knowing is worse than a warning,
# but we don't claim something is broken when we simply couldn't look.
_SEVERITY = {Status.OK: 0, Status.WARN: 1, Status.UNKNOWN: 2, Status.CRIT: 3}


@dataclass(frozen=True)
class Result:
    """The outcome of one check.

    frozen=True makes a Result read-only after it's created, so no later step
    can quietly change a fact the check reported.
    """

    check: str  # what was checked, e.g. "disk:/" or "memory"
    status: Status
    value: float | None  # the measured number (e.g. percent used), None if there isn't one
    detail: str  # one short human-readable sentence

    def to_dict(self) -> dict:
        """Plain dictionary for JSON output (Status becomes its string value)."""
        data = asdict(self)
        data["status"] = self.status.value
        return data


def status_for_percent(percent: float, warn_at: float, crit_at: float) -> Status:
    """Turn a "percent used" number into a status using two thresholds.

    Example with warn_at=80 and crit_at=90:  79.9 -> OK,  80 -> WARN,  95 -> CRIT.
    Shared by every check that measures "how full is it?" (disk, memory, ...).
    """
    if percent >= crit_at:
        return Status.CRIT
    if percent >= warn_at:
        return Status.WARN
    return Status.OK


def worst(results: list[Result]) -> Status:
    """The most serious status among the results (OK if the list is empty)."""
    return max((r.status for r in results), key=_SEVERITY.__getitem__, default=Status.OK)
