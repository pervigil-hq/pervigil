"""Tests for the command-line entry point.

pytest finds every function whose name starts with test_ and runs it.
`capsys` is a pytest helper that captures what the code prints, so we can check it.
"""

import pytest

from pervigil import __version__
from pervigil.cli import main


def test_version_flag_prints_version_and_exits_cleanly(capsys):
    # argparse's version action exits via SystemExit, so we expect that exception.
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"pervigil {__version__}"


def test_no_arguments_shows_help(capsys):
    assert main([]) == 0
    assert "usage: pervigil" in capsys.readouterr().out


def test_collect_prints_a_table_with_overall_status(capsys):
    assert main(["collect"]) == 0
    out = capsys.readouterr().out
    assert "disk:/" in out
    assert "overall:" in out


def test_collect_json_is_valid_json(capsys):
    import json

    assert main(["collect", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["overall"] in {"ok", "warn", "crit", "unknown"}
    assert payload["results"][0]["check"] == "disk:/"


def test_bad_config_exits_with_code_2(tmp_path, capsys):
    bad = tmp_path / "pervigil.toml"
    bad.write_text("[disk]\nwarn_precent = 1\n")
    assert main(["--config", str(bad), "collect"]) == 2
    assert "unknown setting" in capsys.readouterr().err
