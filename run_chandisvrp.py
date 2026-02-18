from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from chandisvrp.cli import run_all


if __name__ == "__main__":
    run_all("configs/benchmark_small.yaml", "reports/interactive_map.html", True)
