"""Tests for loading pervigil.toml.

`tmp_path` is a pytest helper: a fresh empty folder for each test, deleted afterwards.
"""

import pytest

from pervigil import config as config_module
from pervigil.config import Config, ConfigError, load_config


def write(tmp_path, text):
    path = tmp_path / "pervigil.toml"
    path.write_text(text)
    return path


def test_no_file_anywhere_gives_defaults(tmp_path, monkeypatch):
    # point the default location at a file that doesn't exist
    monkeypatch.setattr(config_module, "DEFAULT_CONFIG_PATH", tmp_path / "missing.toml")
    assert load_config() == Config()


def test_partial_file_keeps_other_defaults(tmp_path):
    cfg = load_config(write(tmp_path, '[disk]\npaths = ["/", "/mnt/storage"]\nwarn_percent = 85\n'))
    assert cfg.disk.paths == ["/", "/mnt/storage"]
    assert cfg.disk.warn_percent == 85
    assert cfg.disk.crit_percent == 90  # not in the file, so the default stays
    assert cfg.memory == Config().memory


def test_explicit_path_must_exist(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.toml")


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("[disk\n", "not valid TOML"),
        ("[disk]\nwarn_precent = 85\n", "unknown setting"),  # typo is caught
        ("[dsk]\n", "unknown setting"),
        ("[disk]\nwarn_percent = 95\ncrit_percent = 90\n", "warn_percent < crit_percent"),
        ("[memory]\ncrit_percent = 150\n", "<= 100"),
        ('[memory]\nwarn_percent = "high"\n', "must be numbers"),
        ("[memory]\nwarn_percent = true\n", "must be numbers"),
        ("disk = 5\n", "must be a table"),
    ],
)
def test_bad_config_is_rejected_with_a_clear_message(tmp_path, text, message):
    with pytest.raises(ConfigError, match=message):
        load_config(write(tmp_path, text))
