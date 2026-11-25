"""Tests for the memory check. These are written first: they describe what
"done" means. Run them with:   .venv/bin/pytest tests/test_memory.py -v

Each test writes a fake /proc/meminfo into a temporary folder (tmp_path),
so the expected numbers are known exactly on every machine.
"""

from pathlib import Path

import pytest

from pervigil.checks.memory import MEMINFO, check_memory
from pervigil.result import Status

GIB_IN_KB = 1024 * 1024  # 1 GiB = 1,048,576 kB


def fake_meminfo(tmp_path, total_gib, available_gib, free_gib=1.0):
    """Write a small but realistic meminfo file and return its path."""
    text = (
        f"MemTotal:       {int(total_gib * GIB_IN_KB)} kB\n"
        f"MemFree:        {int(free_gib * GIB_IN_KB)} kB\n"
        f"MemAvailable:   {int(available_gib * GIB_IN_KB)} kB\n"
        "Buffers:          269920 kB\n"
        "Cached:          6994016 kB\n"
    )
    path = tmp_path / "meminfo"
    path.write_text(text)
    return path


def test_normal_usage_is_ok_with_exact_value_and_detail(tmp_path):
    path = fake_meminfo(tmp_path, total_gib=16, available_gib=6)
    result = check_memory(warn_at=85, crit_at=95, meminfo_path=path)
    assert result.check == "memory"
    assert result.value == 62.5  # (16 - 6) / 16 * 100
    assert result.status == Status.OK
    assert result.detail == "62.5% used, 6.0 GiB available"


def test_high_usage_is_warn(tmp_path):
    path = fake_meminfo(tmp_path, total_gib=16, available_gib=2)
    result = check_memory(warn_at=85, crit_at=95, meminfo_path=path)
    assert result.value == 87.5
    assert result.status == Status.WARN


def test_very_high_usage_is_crit_and_rounded(tmp_path):
    path = fake_meminfo(tmp_path, total_gib=16, available_gib=0.5)
    result = check_memory(warn_at=85, crit_at=95, meminfo_path=path)
    assert result.value == 96.9  # 96.875 rounded to 1 decimal
    assert result.status == Status.CRIT


def test_uses_memavailable_not_memfree(tmp_path):
    # Almost no *free* RAM, but plenty *available* (it's just cache): that's healthy.
    path = fake_meminfo(tmp_path, total_gib=16, available_gib=12, free_gib=0.2)
    result = check_memory(warn_at=85, crit_at=95, meminfo_path=path)
    assert result.value == 25.0
    assert result.status == Status.OK


def test_missing_file_is_unknown_not_a_crash(tmp_path):
    result = check_memory(warn_at=85, crit_at=95, meminfo_path=tmp_path / "nope")
    assert result.status == Status.UNKNOWN
    assert result.value is None
    assert result.detail.startswith("can't read")


def test_file_without_memavailable_is_unknown(tmp_path):
    path = tmp_path / "meminfo"
    path.write_text("MemTotal:       16777216 kB\nMemFree:        1048576 kB\n")
    result = check_memory(warn_at=85, crit_at=95, meminfo_path=path)
    assert result.status == Status.UNKNOWN
    assert result.value is None
    assert result.detail.startswith("can't read")


@pytest.mark.skipif(not Path(MEMINFO).exists(), reason="needs Linux /proc/meminfo")
def test_real_meminfo_gives_a_sane_percentage():
    result = check_memory(warn_at=85, crit_at=95)
    assert result.status in {Status.OK, Status.WARN, Status.CRIT}
    assert 0 < result.value < 100
