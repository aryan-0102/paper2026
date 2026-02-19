from __future__ import annotations

import math
import time

import networkx as nx
import numpy as np

from chandisvrp.solvers.base import Solver
from chandisvrp.solvers.constructive import route_length
from chandisvrp.solvers.split import split_by_capacity
from chandisvrp.types import Instance, RoutePlan


class ACOSolver(Solver):
    name = "aco"

    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        cids = [c.customer_id for c in instance.customers]
        node_of = {c.customer_id: c.node for c in instance.customers}
        pher = {cid: 1.0 for cid in cids}
        best_perm = cids[:]

        def score(perm: list[int]) -> float:
            routes = split_by_capacity(perm, instance.customers, instance.vehicle_capacity)
            return sum(route_length(r, g, node_of, instance.depot_node) for r in routes)

        best_score = score(best_perm)
        start = time.time()
        while time.time() - start < time_limit_s:
            ants: list[list[int]] = []
            for _ in range(8):
                rem = set(cids)
                perm: list[int] = []
                while rem:
                    vals = np.array([pher[c] for c in rem], dtype=float)
                    p = vals / vals.sum()
                    choice = list(rem)[int(rng.choice(len(rem), p=p))]
                    perm.append(choice)
                    rem.remove(choice)
                ants.append(perm)
            for perm in ants:
                sc = score(perm)
                if sc < best_score:
                    best_perm, best_score = perm, sc
                for c in perm:
                    pher[c] = 0.95 * pher[c] + 0.05 * (1.0 / (1.0 + sc))
            for c in pher:
                pher[c] = max(1e-6, pher[c] * 0.995)
        return RoutePlan(routes=split_by_capacity(best_perm, instance.customers, instance.vehicle_capacity))
