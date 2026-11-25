"""Memory check: how much of the RAM is really in use?

How Linux reports memory
------------------------
The file /proc/meminfo is not a real file on disk: the kernel generates it
every time it is read. Each line looks like this (values are in kibibytes, kB):

    MemTotal:       31754312 kB
    MemFree:        20548768 kB
    MemAvailable:   27507540 kB
    ...

We use MemAvailable, not MemFree. MemFree only counts completely unused RAM,
but Linux fills spare RAM with cache (recently read files) and drops that cache
instantly when a program needs memory. So a healthy server often shows very
little *free* memory; MemAvailable is the kernel's estimate of what programs
can really still use (free RAM plus reclaimable cache).

    percent used = (MemTotal - MemAvailable) / MemTotal * 100
"""

from pathlib import Path

from pervigil.result import Result, Status, status_for_percent

MEMINFO = Path("/proc/meminfo")


def check_memory(warn_at: float, crit_at: float, meminfo_path: Path = MEMINFO) -> Result:
    """Return one Result named "memory" with the percent of RAM in use.

    meminfo_path is a parameter so tests can hand in a fake file instead of the real one.

    Expected results (the tests check these exactly):
      - check:  "memory"
      - value:  percent used, rounded to 1 decimal (e.g. 62.5)
      - status: from status_for_percent(value, warn_at, crit_at)
      - detail: "62.5% used, 6.0 GiB available"  (available = MemAvailable in GiB, 1 decimal)
      - if the file can't be read, or MemTotal/MemAvailable is missing:
        status UNKNOWN, value None, and a detail starting with "can't read"
    """
    name = "memory"
    # Read the file; if it's missing or unreadable, report UNKNOWN instead of crashing.
    try:
        text = meminfo_path.read_text()
    except OSError as e:
        return Result(name, Status.UNKNOWN, None, f"can't read {meminfo_path}: {e.strerror or e}")

    # Parse lines like "MemTotal:   31754312 kB" into {"MemTotal": 31754312, ...} (values in kB).
    info = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        key = parts[0].rstrip(":")
        value = int(parts[1])
        info[key] = value

    # Both values are required; total = 0 would also make the percentage meaningless.
    total = info.get("MemTotal")
    available = info.get("MemAvailable")
    if total in (None, 0) or available is None:
        return Result(
            name, Status.UNKNOWN, None, f"can't read MemTotal/MemAvailable from {meminfo_path}"
        )

    # Percent used, plus available memory in GiB for the human-readable detail.
    percent = round((total - available) / total * 100, 1)
    available_gib = available / 1024 / 1024
    status = status_for_percent(percent, warn_at, crit_at)
    return Result(
        check=name,
        status=status,
        value=percent,
        detail=f"{percent}% used, {available_gib:.1f} GiB available",
    )
