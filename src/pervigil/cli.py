"""Command-line entry point: what runs when you type `pervigil`.

Subcommands:
  pervigil collect          run the checks and print the results
  pervigil collect --json   the same, as JSON (for scripts and, later, the digest)
"""

import argparse
import json
import sys
from pathlib import Path

from pervigil import __version__
from pervigil.checks.disk import check_disk
from pervigil.config import Config, ConfigError, load_config
from pervigil.result import Result, worst


def build_parser() -> argparse.ArgumentParser:
    """Describe the command line: program name, help text, options and subcommands.

    Kept separate from main() so tests can inspect the parser without running anything.
    """
    parser = argparse.ArgumentParser(
        prog="pervigil",
        description="A watchful morning report for your self-hosted server.",
    )
    # action="version" prints the text and exits, so no extra code is needed.
    parser.add_argument("--version", action="version", version=f"pervigil {__version__}")
    parser.add_argument(
        "--config", type=Path, help="path to pervigil.toml (default: ~/.config/pervigil/)"
    )

    sub = parser.add_subparsers(dest="command")
    collect = sub.add_parser("collect", help="run the checks and print the results")
    collect.add_argument("--json", action="store_true", help="print JSON instead of a table")
    return parser


def run_checks(config: Config) -> list[Result]:
    """Run every check with its settings from the config, in a fixed order."""
    results: list[Result] = []
    results += check_disk(config.disk.paths, config.disk.warn_percent, config.disk.crit_percent)
    # TODO (last step of the memory task): add the memory check here, using config.memory.
    return results


def format_table(results: list[Result]) -> str:
    """Human-readable output: one line per check, worst status at the end."""
    lines = [f"{r.status.value.upper():8} {r.check:20} {r.detail}" for r in results]
    lines.append(f"overall: {worst(results).value}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments and run the chosen command.

    argv=None means "use the real command line" (sys.argv); tests pass a list instead.
    Returns the process exit code: 0 success, 2 bad config or usage.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()  # no subcommand given: show what is available
        return 0

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"pervigil: {e}", file=sys.stderr)
        return 2

    if args.command == "collect":
        results = run_checks(config)
        if args.json:
            payload = {"overall": worst(results).value, "results": [r.to_dict() for r in results]}
            print(json.dumps(payload, indent=2))
        else:
            print(format_table(results))
    return 0


if __name__ == "__main__":
    # Allows `python -m pervigil.cli` as well as the installed `pervigil` command.
    raise SystemExit(main())
