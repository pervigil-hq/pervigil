"""Load the settings from pervigil.toml, falling back to safe defaults.

Pervigil works without any config file: every setting has a default. A config
file only needs the values someone wants to change, for example:

    [disk]
    paths = ["/", "/mnt/storage"]
    warn_percent = 85

Unknown settings are an error rather than silently ignored, so a typo like
`warn_precent` is caught instead of leaving the default in place unnoticed.
"""

import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

# Where Pervigil looks when no --config path is given.
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "pervigil" / "pervigil.toml"


class ConfigError(Exception):
    """The config file exists but can't be used (bad TOML, typo, impossible value)."""


@dataclass(frozen=True)
class DiskConfig:
    paths: list[str] = field(default_factory=lambda: ["/"])  # mount points to check
    warn_percent: float = 80
    crit_percent: float = 90


@dataclass(frozen=True)
class MemoryConfig:
    warn_percent: float = 85
    crit_percent: float = 95


@dataclass(frozen=True)
class Config:
    disk: DiskConfig = field(default_factory=DiskConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)


def load_config(path: Path | None = None) -> Config:
    """Read the config file and return a Config.

    - path given: that file must exist.
    - no path: use DEFAULT_CONFIG_PATH if it exists, otherwise all defaults.
    """
    if path is None:
        if not DEFAULT_CONFIG_PATH.exists():
            return Config()
        path = DEFAULT_CONFIG_PATH

    try:
        with path.open("rb") as f:  # tomllib needs the file opened in binary mode
            raw = tomllib.load(f)
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path} is not valid TOML: {e}") from None

    _reject_unknown(raw, {"disk", "memory"}, where="top level")
    disk = _build_section(DiskConfig, raw.get("disk", {}), "disk")
    memory = _build_section(MemoryConfig, raw.get("memory", {}), "memory")
    return Config(disk=disk, memory=memory)


def _build_section(cls, values: dict, name: str):
    """Create one config section (e.g. DiskConfig) from its TOML table, then check it."""
    if not isinstance(values, dict):
        raise ConfigError(f"[{name}] must be a table")
    _reject_unknown(values, {f.name for f in fields(cls)}, where=f"[{name}]")
    section = cls(**values)  # settings not given keep their defaults
    _check_thresholds(section.warn_percent, section.crit_percent, name)
    return section


def _reject_unknown(values: dict, allowed: set[str], where: str) -> None:
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ConfigError(f"unknown setting(s) in {where}: {', '.join(unknown)}")


def _check_thresholds(warn: float, crit: float, name: str) -> None:
    """Thresholds must be numbers between 0 and 100, and warn must come before crit."""
    for value in (warn, crit):
        # bool is a subclass of int in Python, so `true` would sneak through without this
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ConfigError(f"[{name}] thresholds must be numbers, got {value!r}")
    if not 0 <= warn < crit <= 100:
        raise ConfigError(
            f"[{name}] needs 0 <= warn_percent < crit_percent <= 100 (got {warn} and {crit})"
        )
