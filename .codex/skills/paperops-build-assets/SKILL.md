---
name: paperops-build-assets
description: Rebuild paper assets (figures/tables/variables) deterministically for a paper_id and confirm synchronization with checks.
---

# Inputs
- paper_id

# Rules
- You MUST run: `uv run paperops build-paper-assets --paper <paper_id>`
- You MUST NOT manually edit generated outputs under `papers/<paper_id>/auto/`.
- You MUST NOT edit any non-allowed files in AGENTS.md.
- If build_toggle/config changes are needed but not allowed, propose a patch plan only.

# What you must output
1) **Build result**
   - Success/Fail
   - If Fail: the most relevant error lines and likely cause
2) **What changed**
   - List which asset categories likely updated (variables/figures/tables) based on build logs / file timestamps
3) **Verification**
   - Run: `uv run paperops check --paper <paper_id> --mode ci`
   - Report PASS/FAIL and next action if FAIL

# Common remediation playbook
- If build fails due to missing experiment outputs:
  - Provide commands to run the needed experiment first:
    `uv run paperops run exp=<exp_name>`
  - Then rebuild assets again.
- If build fails due to environment/deps:
  - Provide exact missing package/error and suggest minimal `uv` steps.
