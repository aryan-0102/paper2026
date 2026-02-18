from __future__ import annotations

import math

import networkx as nx


def nearest_node(g: nx.MultiDiGraph, x: float, y: float) -> int:
    best = None
    best_d = float("inf")
    for n, data in g.nodes(data=True):
        dx = float(data.get("x", 0.0)) - x
        dy = float(data.get("y", 0.0)) - y
        d = math.hypot(dx, dy)
        if d < best_d:
            best_d = d
            best = n
    assert best is not None
    return int(best)
