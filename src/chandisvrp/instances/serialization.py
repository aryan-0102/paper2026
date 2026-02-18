from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from chandisvrp.types import Customer, Instance


def save_instance(instance: Instance, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(instance), indent=2))


def load_instance(path: str | Path) -> Instance:
    data = json.loads(Path(path).read_text())
    customers = [Customer(**c) for c in data["customers"]]
    data["customers"] = customers
    return Instance(**data)
