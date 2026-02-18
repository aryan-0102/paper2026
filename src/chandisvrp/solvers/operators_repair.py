from __future__ import annotations

import numpy as np


def greedy_repair(routes: list[list[int]], removed: list[int], rng: np.random.Generator) -> list[list[int]]:
    if not routes:
        routes = [[]]
    for c in removed:
        idx = int(rng.integers(0, len(routes)))
        pos = int(rng.integers(0, len(routes[idx]) + 1))
        routes[idx].insert(pos, c)
    return routes
