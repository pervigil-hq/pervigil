# Pervigil

> *pervigil* (Latin): "keeping watch all night through."
> Pervigil watches your self-hosted server overnight and hands you a short, honest report in the morning.

**Status: early development, nothing to install yet.** This README is also the project plan and scope contract: if a feature isn't in "What v0.1 does", it waits. Once v0.1 ships, the plan moves to `ROADMAP.md` and this page becomes the user guide.

> **A student project, built in the open.** Pervigil is a learning project by a cyber-security student. The goal is a genuinely useful tool *and* code that is easy to read and understand. Feedback of any kind is very welcome, whether that's a bug, a design you'd do differently, a check you wish existed, or "this part was hard to follow". Open an issue or a discussion.

## The problem
People who run their own server (a homelab, a VPS, a small business box) usually have graphs (Beszel, Netdata) and uptime checks (Uptime Kuma). What they don't have is someone who asks every morning: **"Is anything wrong, and did anything change that I didn't expect?"** A new open port, a service that got enabled by an update, a hardening setting that reverted after a reboot, a backup that quietly stopped. Graphs don't tell you that; you have to go looking.

## Who it's for
One person looking after one Linux server: homelabbers, self-hosters, students, small-business admins. Comfortable with a terminal, not wanting to run a monitoring stack.

## What v0.1 does
- **Health checks:** disk, memory, CPU temperature, Docker containers (running, healthy, restarting), pending updates and reboot-required, optional backup freshness.
- **Drift detection:** records a known-good **baseline** (listening ports, enabled systemd units, containers), then reports anything new or missing. A new port on a public address is critical. The user reviews and approves changes (`pervigil drift --diff` / `--approve`).
- **Morning digest:** one short report (Markdown + push notification via ntfy): what needs attention, what recovered, trends.
- **Optional AI narration:** if a local LLM is configured (Ollama or any OpenAI-compatible endpoint), it rewrites the digest in plain English. Off by default.
- **Alerts:** push on critical, on recovery, and a reminder if something stays broken.
- **Install:** one script, runs from cron as a normal user. Ubuntu 24.04+ / Debian 12+.

## What makes it different
1. **The script decides, the AI only words it.** Severity is fixed code, never the model's opinion.
2. **AI that can't lie to you.** Every AI answer is checked by a validator: same items, same severities, no numbers that aren't in the facts. If it fails, you get the plain template instead. Tested with prompt-injection attacks hidden in the data.
3. **Works fully without AI.** The template digest is the default and always correct.
4. **Read-only, always.** Pervigil observes and reports. It never changes your system.

## Not in v0.1 (non-goals)
Log triage · job queue · web dashboard · multiple servers · root-only checks (SMART, firewall rules) · distros other than Ubuntu/Debian · paid/hosted tier · auto-fixing anything.
These are candidates for v0.2+, decided by what users actually ask for.

## How it works
```
cron (hourly)          cron (daily)
     |                      |
  collect  --> results --> digest --> [optional LLM --> validator] --> report.md
     |          (JSON)        |                                         |
  checks/                  facts                                     notify (ntfy)
  baseline (drift)
```
Each check is a small function returning the same shape: `Result(name, status, value, detail)`, where status is `ok | warn | crit | unknown`. Learn one check, and you understand them all.

## Design principles
- **Python 3.11+, standard library only.** No dependencies to install or audit (`tomllib` for config, `urllib` for HTTP).
- **One config file** (`pervigil.toml`), sensible defaults, secrets (ntfy token) from environment variables only.
- **Explainable code:** small functions, type hints, docstrings that explain *why*, plain English names (the Latin stays in the name). `ruff` for style, `pytest` for tests.
- **Data stays local.** No telemetry. Cloud LLM endpoints work but print a warning: your server data would leave the machine.

## Done means (v0.1 success criteria)
- Installs on a fresh Ubuntu and Debian VM in under 5 minutes, and `pervigil doctor` passes.
- All checks and the validator have tests; CI is green; the injection tests pass.
- README, ARCHITECTURE.md, THREAT_MODEL.md, SECURITY.md, and decision records written.
- The maintainer can explain every module, and why it is built that way, without notes.
- Replaces the original janitor on the author's own homelab.

## Plan (~10 h/week, 6-8 weeks)
| Step | Content |
|---|---|
| A1 | Repo, licence (MIT), CI skeleton, gitleaks, this brief, project layout |
| A2 | `Result` model, config loading, first checks (disk, memory) end to end |
| A3 | Remaining checks + drift baseline |
| A4 | Digest: template, optional LLM, validator, ntfy notify, tests incl. injection |
| A5 | Installer, `doctor`, VM tests, docs, v0.1.0 release + launch post |

## How we work
Small pull requests, one feature each. Every piece is written or reviewed by the maintainer and **explained back before it merges** (AI-assisted development, human-understood code). Design choices get a short decision record in `docs/decisions/`.

## Open questions
- Exact container checks without Docker installed (skip cleanly?).
- Python version floor: 3.11 (Debian 12) vs 3.12 (Ubuntu 24.04).
- Notification channels beyond ntfy (email? Discord?) after v0.1.

## Origin
Pervigil began as a homelab script called *janitor*, from Latin *ianitor*, the doorkeeper. It grew a validator after a small local model happily labelled an injected "mark this as noise" line as noise. The rewrite keeps the idea and makes it something anyone can install and understand.
