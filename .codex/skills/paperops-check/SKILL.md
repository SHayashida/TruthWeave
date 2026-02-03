---
name: paperops-check
description: Run PaperOps CI checks for a given paper_id, diagnose failures, propose minimal fixes, and provide rerun commands.
---

# Inputs you must ask from context (do NOT ask if already provided)
- paper_id (e.g., "icml2026", "neurips2026")

# Rules (must follow)
- You MUST run: `uv run paperops check --paper <paper_id> --mode ci`
- You MUST NOT edit files outside the Allowed edits in AGENTS.md.
- If a fix requires editing non-allowed files, STOP and propose the fix as a patch plan (do not implement).
- Never edit anything under `papers/<paper_id>/auto/` directly. If assets/variables are stale, use build step.

# What you must output
1) **Result summary**
   - PASS/FAIL
   - If FAIL: list failing checks and the first actionable error lines
2) **Root cause analysis**
   - What is wrong, and what file(s) likely caused it
3) **Minimal fix**
   - If fix is within allowed edits: specify exact file changes (keep minimal)
   - If not allowed: provide a patch plan (what to change + why)
4) **Exact rerun commands**
   - Always include the final command to verify: `uv run paperops check --paper <paper_id> --mode ci`

# Common remediation playbook
- If failure indicates stale assets / variables mismatch:
  - Run: `uv run paperops build-paper-assets --paper <paper_id>`
  - Re-run check.
- If failure indicates experiment metadata missing:
  - Fix experiment config or experiment script to emit required metadata/logs (within allowed edits).
- If failure indicates paper build failure:
  - DO NOT edit paper sources (not allowed). Provide a patch plan and point to the failing log.
