from __future__ import annotations

import re
from pathlib import Path


def check(tex_path: Path) -> None:
    if not tex_path.exists():
        raise SystemExit("Missing paper/main.tex")

    decimal_pattern = re.compile(r"\b\d+\.\d+\b")
    percent_pattern = re.compile(r"\b\d+%")

    violations = []
    for idx, raw_line in enumerate(tex_path.read_text().splitlines(), start=1):
        if "paperops-allow-number" in raw_line:
            continue
        line = raw_line.split("%", 1)[0]
        if decimal_pattern.search(line) or percent_pattern.search(line):
            violations.append(f"line {idx}: {raw_line.strip()}")

    if violations:
        message = "Manual numbers detected in paper/main.tex:\n" + "\n".join(
            violations
        )
        raise SystemExit(message)
