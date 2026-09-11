# Claude Code Agent Instructions — Orion Backend

Welcome. You are operating on the **Orion World State Engine backend** (fork repository).

## Universal AI Agent System
This codebase uses a centralized, first-principles AI context system located in `.ai/`.

Before making changes or answering architectural questions, read:
1. [`.ai/README.md`](.ai/README.md) — Master index and quick orientation.
2. [`.ai/PHILOSOPHY.md`](.ai/PHILOSOPHY.md) — First-principles engineering philosophy.
3. [`.ai/RULES.md`](.ai/RULES.md) — Mandatory non-negotiable rules (rule-based consistency, tenant isolation, append-only facts).
4. [`.ai/WORKFLOW.md`](.ai/WORKFLOW.md) — Git fork conventions and branching.

## Essential Commands
```bash
# Run test suite
PYTHONPATH=backend pytest app/tests/ -v

# Start local server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
