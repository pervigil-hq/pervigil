"""Tests for the Result model and the threshold helpers."""

import json

import pytest

from pervigil.result import Result, Status, status_for_percent, worst


@pytest.mark.parametrize(
    ("percent", "expected"),
    [
        (0, Status.OK),
        (79.9, Status.OK),
        (80, Status.WARN),  # the threshold itself already counts as WARN
        (89.9, Status.WARN),
        (90, Status.CRIT),
        (100, Status.CRIT),
    ],
)
def test_status_for_percent_uses_both_thresholds(percent, expected):
    # parametrize runs this one test once per (percent, expected) pair above
    assert status_for_percent(percent, warn_at=80, crit_at=90) == expected


def test_worst_picks_the_most_serious_status():
    results = [
        Result("a", Status.OK, 1, ""),
        Result("b", Status.WARN, 2, ""),
        Result("c", Status.UNKNOWN, None, ""),
    ]
    assert worst(results) == Status.UNKNOWN  # unknown ranks above warn
    assert worst(results + [Result("d", Status.CRIT, 3, "")]) == Status.CRIT


def test_worst_of_nothing_is_ok():
    assert worst([]) == Status.OK


def test_result_is_read_only():
    r = Result("disk:/", Status.OK, 10, "fine")
    with pytest.raises(AttributeError):  # frozen dataclass refuses changes
        r.status = Status.CRIT


def test_result_to_dict_is_json_ready():
    r = Result("memory", Status.WARN, 87.5, "87.5% used")
    assert json.loads(json.dumps(r.to_dict())) == {
        "check": "memory",
        "status": "warn",
        "value": 87.5,
        "detail": "87.5% used",
    }
