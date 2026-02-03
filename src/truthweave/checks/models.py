from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Issue:
    category: str
    severity: str
    message: str
    fix: Optional[str]
    recheck: Optional[str]
    paths: List[str]
