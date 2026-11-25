"""Command-line entry point: what runs when you type `pervigil`.

For now it only knows `--version`. Later steps add subcommands such as
`pervigil collect`, `pervigil digest` and `pervigil drift`.
"""

import argparse

from pervigil import __version__


def build_parser() -> argparse.ArgumentParser:
    """Describe the command line: program name, help text and options.

    Kept separate from main() so tests can inspect the parser without running anything.
    """
    parser = argparse.ArgumentParser(
        prog="pervigil",
        description="A watchful morning report for your self-hosted server.",
    )
    # action="version" prints the text and exits, so no extra code is needed.
    parser.add_argument("--version", action="version", version=f"pervigil {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments and run the chosen command.

    argv=None means "use the real command line" (sys.argv); tests pass a list instead.
    Returns the process exit code: 0 means success.
    """
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()  # no subcommands yet, so show what is available
    return 0


if __name__ == "__main__":
    # Allows `python -m pervigil.cli` as well as the installed `pervigil` command.
    raise SystemExit(main())
