"""Health checks. Each module exposes one function that returns Result(s).

Checks only *observe*: they read files and ask the system questions, and they
never change anything (read-only by design, see README).
"""
