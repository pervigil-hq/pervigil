"""Tests for the disk check.

The real disk is whatever the test machine has, so the tests replace
shutil.disk_usage with a fake (monkeypatch) that returns numbers we choose.
"""

import shutil
from collections import namedtuple

from pervigil.checks.disk import check_disk
from pervigil.result import Status

Usage = namedtuple("Usage", "total used free")
GIB = 1024**3


def fake_usage(used_gib, free_gib):
    def _disk_usage(path):
        return Usage(total=used_gib + free_gib + 5 * GIB, used=used_gib * GIB, free=free_gib * GIB)

    return _disk_usage


def test_percent_matches_df_and_status_follows_thresholds(monkeypatch):
    monkeypatch.setattr(shutil, "disk_usage", fake_usage(used_gib=85, free_gib=15))
    [result] = check_disk(["/"], warn_at=80, crit_at=90)
    assert result.check == "disk:/"
    assert result.value == 85.0  # used / (used + free), ignoring root-reserved blocks
    assert result.status == Status.WARN
    assert result.detail == "85.0% used, 15.0 GiB free"


def test_one_result_per_path(monkeypatch):
    monkeypatch.setattr(shutil, "disk_usage", fake_usage(used_gib=10, free_gib=90))
    results = check_disk(["/", "/mnt/storage"], warn_at=80, crit_at=90)
    assert [r.check for r in results] == ["disk:/", "disk:/mnt/storage"]
    assert all(r.status == Status.OK for r in results)


def test_missing_path_is_unknown_not_a_crash():
    [result] = check_disk(["/definitely/not/a/real/path"], warn_at=80, crit_at=90)
    assert result.status == Status.UNKNOWN
    assert result.value is None
    assert "can't read" in result.detail
