from __future__ import annotations

import math

import networkx as nx
import numpy as np

from chandisvrp.solvers.base import Solver
from chandisvrp.solvers.split import split_by_capacity
from chandisvrp.types import Instance, RoutePlan


def _coords(g: nx.MultiDiGraph, node: int) -> tuple[float, float]:
    d = g.nodes[node]
    return float(d.get("x", 0.0)), float(d.get("y", 0.0))


def _dist(g: nx.MultiDiGraph, a: int, b: int) -> float:
    ax, ay = _coords(g, a)
    bx, by = _coords(g, b)
    return math.hypot(ax - bx, ay - by)


def two_opt(route: list[int], g: nx.MultiDiGraph, node_of: dict[int, int], depot: int) -> list[int]:
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j][::-1] + best[j:]
                if route_length(cand, g, node_of, depot) < route_length(best, g, node_of, depot):
                    best = cand
                    improved = True
    return best


def route_length(route: list[int], g: nx.MultiDiGraph, node_of: dict[int, int], depot: int) -> float:
    cur = depot
    total = 0.0
    for cid in route:
        n = node_of[cid]
        total += _dist(g, cur, n)
        cur = n
    total += _dist(g, cur, depot)
    return total


class NearestNeighbor2OptSolver(Solver):
    name = "nn2opt"

    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        remaining = set(c.customer_id for c in instance.customers)
        node_of = {c.customer_id: c.node for c in instance.customers}
        order: list[int] = []
        cur = instance.depot_node
        while remaining:
            nxt = min(remaining, key=lambda cid: _dist(g, cur, node_of[cid]))
            order.append(nxt)
            cur = node_of[nxt]
            remaining.remove(nxt)
        routes = split_by_capacity(order, instance.customers, instance.vehicle_capacity)
        routes = [two_opt(r, g, node_of, instance.depot_node) if len(r) > 3 else r for r in routes]
        return RoutePlan(routes=routes)
