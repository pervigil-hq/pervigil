"""Disk check: how full is each configured mount point?

This is the pattern every "how full is it?" check follows:
  1. measure the number,
  2. turn it into a status with the shared thresholds helper,
  3. return a Result with a short, readable detail.
"""

import shutil

from pervigil.result import Result, Status, status_for_percent


def check_disk(paths: list[str], warn_at: float, crit_at: float) -> list[Result]:
    """Return one Result per path, e.g. check "disk:/" with value 42.5 (percent used)."""
    return [_check_one(path, warn_at, crit_at) for path in paths]


def _check_one(path: str, warn_at: float, crit_at: float) -> Result:
    name = f"disk:{path}"
    try:
        usage = shutil.disk_usage(path)  # total, used and free space in bytes
    except OSError as e:  # path missing, not mounted, no permission, ...
        return Result(name, Status.UNKNOWN, None, f"can't read {path}: {e.strerror or e}")

    # Same formula as `df`: used / (used + free). Linux keeps some blocks reserved for
    # root, so used / total would look a few percent emptier than `df` reports.
    percent = round(usage.used / (usage.used + usage.free) * 100, 1)
    free_gb = usage.free / 1024**3
    return Result(
        check=name,
        status=status_for_percent(percent, warn_at, crit_at),
        value=percent,
        detail=f"{percent}% used, {free_gb:.1f} GiB free",
    )
