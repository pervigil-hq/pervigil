# Decision records

Short notes that explain **why** Pervigil is built the way it is. Each one records a single decision: the situation, what was decided, and what it costs. They are written when the decision is made, so the reasoning isn't lost later.

Numbered in order; never renumbered. A decision that changes later gets a new record that *supersedes* the old one, and the old one stays for history.

| # | Decision | Status |
|---|---|---|
| [0001](0001-llm-never-decides-severity.md) | The language model never decides severity | Accepted |
| [0002](0002-standard-library-only.md) | Standard library only, no runtime dependencies | Accepted |

## Template

```markdown
# NNNN. Title in a few words

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD

## Context
What situation or problem forces a choice?

## Decision
What we do, in one or two sentences.

## Consequences
What gets better, what gets worse, what we must now do.

## Alternatives considered
What else was possible, and why not.
```
