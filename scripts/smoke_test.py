from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from chandisvrp.cli import run_all


def main() -> None:
    cfg = "configs/benchmark_small.yaml"
    run_all(cfg, "reports/interactive_map.html", False)
    print("Smoke test completed")


if __name__ == "__main__":
    main()
