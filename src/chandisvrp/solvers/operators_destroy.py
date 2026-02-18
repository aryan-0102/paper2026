from __future__ import annotations

import numpy as np


def random_destroy(routes: list[list[int]], rng: np.random.Generator, fraction: float = 0.2) -> tuple[list[list[int]], list[int]]:
    flat = [c for r in routes for c in r]
    k = max(1, int(len(flat) * fraction))
    removed = list(rng.choice(flat, size=min(k, len(flat)), replace=False))
    new_routes = [[c for c in r if c not in removed] for r in routes]
    return [r for r in new_routes if r], removed
