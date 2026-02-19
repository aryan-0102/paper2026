from __future__ import annotations

import time

import networkx as nx
import numpy as np

from chandisvrp.solvers.base import Solver
from chandisvrp.solvers.constructive import route_length
from chandisvrp.solvers.split import split_by_capacity
from chandisvrp.types import Instance, RoutePlan


class ABCSolver(Solver):
    name = "abc"

    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        cids = [c.customer_id for c in instance.customers]
        node_of = {c.customer_id: c.node for c in instance.customers}
        best = cids[:]
        start = time.time()

        def score(perm: list[int]) -> float:
            routes = split_by_capacity(perm, instance.customers, instance.vehicle_capacity)
            return sum(route_length(r, g, node_of, instance.depot_node) for r in routes)

        best_s = score(best)
        while time.time() - start < time_limit_s:
            cand = best[:]
            i, j = rng.integers(0, len(cand), size=2)
            cand[i], cand[j] = cand[j], cand[i]
            sc = score(cand)
            if sc < best_s:
                best, best_s = cand, sc
        return RoutePlan(routes=split_by_capacity(best, instance.customers, instance.vehicle_capacity))
