"""Memory check: how much of the RAM is really in use?

YOUR TASK: implement check_memory() below so that tests/test_memory.py passes.
Follow the same pattern as checks/disk.py: measure -> status -> Result.

How Linux reports memory
------------------------
The file /proc/meminfo is not a real file on disk: the kernel generates it
every time it is read. Each line looks like this (values are in kibibytes, kB):

    MemTotal:       31754312 kB
    MemFree:        20548768 kB
    MemAvailable:   27507540 kB
    ...

Use MemTotal and **MemAvailable**, not MemFree. (Think about why before you
look it up: what does Linux do with RAM nobody is using? Hint: `Cached:`.)

    percent used = (MemTotal - MemAvailable) / MemTotal * 100
"""

from pathlib import Path

from pervigil.result import Result, Status, status_for_percent  # noqa: F401  (you'll need these)

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
    # TODO 1: read the text of meminfo_path.
    #         If that fails with OSError, return an UNKNOWN Result (see disk.py for an example).
    #
    # TODO 2: turn the lines into a dictionary, e.g. {"MemTotal": 31754312, "MemFree": ...}.
    #         Each line is "Name:   12345 kB". str.split() is your friend:
    #         "MemTotal:   31754312 kB".split()  ->  ["MemTotal:", "31754312", "kB"]
    #
    # TODO 3: get MemTotal and MemAvailable from the dictionary.
    #         If either is missing, return an UNKNOWN Result.
    #
    # TODO 4: calculate the percent used (formula in the module docstring), rounded to 1 decimal,
    #         and the available memory in GiB (kB -> GiB: divide by 1024 twice).
    #
    # TODO 5: return the Result, using status_for_percent() for the status.
    raise NotImplementedError("check_memory is your task, see the TODOs above")
