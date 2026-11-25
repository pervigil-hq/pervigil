# 0002. Standard library only, no runtime dependencies

- **Status:** Accepted
- **Date:** 2026-11-25

## Context
Pervigil runs on the server it watches, often with access to sensitive information. Every third-party package is code that runs there, has to be trusted and updated, and can be hijacked (supply-chain attacks). Users also need an easy install on a plain Ubuntu or Debian server.

## Decision
**Pervigil uses only Python's standard library at runtime** (Python 3.11+): `tomllib` for the config file, `urllib` for HTTP (ntfy, the LLM endpoint), `argparse` for the command line, `json`, `subprocess`, `pathlib` and friends for the rest.

Developer tools (ruff, pytest) are fine, because they never run on users' servers. They are pinned to exact versions.

## Consequences
- Installing needs nothing beyond Python itself; there are no dependencies to audit or keep updated.
- Some code is a little longer than with a library (for example HTTP requests with `urllib` instead of `requests`). That's accepted, and it keeps everything readable in one place.
- Adding a runtime dependency later needs a new decision record explaining why it's worth it.

## Alternatives considered
- **`requests`, `pydantic`, `rich`, `click`:** nicer APIs, but each adds supply-chain risk and install friction for small gains. Rejected for now.
- **Writing it in Go (single binary):** easy to distribute, but less approachable for contributors and for the maintainer's learning goals. Rejected.
