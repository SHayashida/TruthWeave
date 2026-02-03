# AGENTS.md — PaperOps Agent Contract (Template Repo)

## Mission
You are operating inside a PaperOps template repository.
Your goal is to help with reproducible, auditable paper workflows without breaking the template structure.

## Non-negotiables (safety rails)
- Never fabricate results, citations, or file contents. If unsure, propose a verification plan.
- Keep changes minimal and reviewable (small diffs).
- Do not move/rename directories or restructure the project.
- Do not manually edit auto-generated outputs under `papers/<paper_id>/auto/` (these must be produced by build steps).

## Allowed edits (STRICT)
Unless the user explicitly asks otherwise, you may ONLY edit:
- `conf/exp/<exp_name>.yaml`
- `src/paperops/experiments/<exp_name>.py`
- Files under `.codex/skills/**` (to maintain skills)
- `AGENTS.md` itself

Everything else is read-only by default.

## Core commands (single source of truth)
- Run experiment: `uv run paperops run exp=<exp_name>`
- Discover: `uv run paperops discover`
- Build paper assets: `uv run paperops build-paper-assets --paper <paper_id>`
- Check: `uv run paperops check --paper <paper_id> --mode ci`
- Build PDF: `uv run paperops build-paper --paper <paper_id>`

## Definition of done for any change
- `uv run paperops check --paper <paper_id> --mode ci` passes (or you explain exactly why it cannot).
- Any new/updated result is traceable to a run (config/seed/git hash) and appears via generated assets/variables, not manual paper edits.

## Interaction style
- When you propose edits, show:
  1) What failed and why
  2) Minimal fix (files + diff summary)
  3) Exact commands to re-run
