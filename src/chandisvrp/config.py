from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def load_config(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    cfg = yaml.safe_load(p.read_text()) or {}
    inherit = cfg.get("inherits")
    if inherit:
        parent_path = Path(inherit)
        if not parent_path.is_absolute():
            parent_path = p.parent / parent_path
        parent = load_config(parent_path)
        cfg = deep_merge(parent, {k: v for k, v in cfg.items() if k != "inherits"})
    return cfg
