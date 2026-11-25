# Security policy

Pervigil reads sensitive facts about a server (open ports, services, containers) and can send them to a language model and a push service. Security reports are taken seriously, even though this is a small student project.

## Reporting a vulnerability

**Please don't open a public issue for security problems.**
Use GitHub's private reporting instead: **[Report a vulnerability](https://github.com/pervigil-hq/pervigil/security/advisories/new)** (the *Security* tab, then *Report a vulnerability*). Only the maintainer can see the report.

Helpful to include: what you found, how to reproduce it, the version or commit, and what an attacker could do with it.

## What to expect

This is a one-person project run in spare time, so responses are best effort:
- acknowledgement within **7 days**,
- a fix or a plan within **30 days** for confirmed issues, sooner for serious ones,
- credit in the release notes if you'd like it.

## Supported versions

Pervigil is pre-1.0. Only the latest release (and `main`) gets security fixes.

## In scope

- Anything that lets untrusted input (logs, container names, file names, model output) make Pervigil run commands, write outside its own folders, or report something false as fact.
- Leaks of server details beyond the configured report and notification targets.
- Ways around the validator that checks AI-written digests.

## Out of scope

- Problems in the services Pervigil reports on (Docker, systemd and so on): report those upstream.
- A language model writing clumsy prose, as long as the validated facts stay correct.
