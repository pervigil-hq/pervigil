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
