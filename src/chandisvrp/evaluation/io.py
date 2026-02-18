from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def ensure_parent(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_results(df: pd.DataFrame, path: str | Path) -> None:
    ensure_parent(path)
    df.to_csv(path, index=False)


def write_metadata(data: dict, path: str | Path) -> None:
    p = ensure_parent(path)
    p.write_text(json.dumps(data, indent=2, default=str))
