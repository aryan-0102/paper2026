from __future__ import annotations

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
        if not cids:
            return RoutePlan(routes=[], meta={"iterations": 0, "improvements": 0})
        node_of = {c.customer_id: c.node for c in instance.customers}
        pher = {cid: 1.0 for cid in cids}
        best_perm = cids[:]
        ants_per_iter = 8
        iterations = 0
        improvements = 0

        def score(perm: list[int]) -> float:
            routes = split_by_capacity(perm, instance.customers, instance.vehicle_capacity)
            return sum(route_length(r, g, node_of, instance.depot_node) for r in routes)

        def weighted_permutation() -> list[int]:
            vals = np.array([max(1e-12, pher[c]) for c in cids], dtype=float)
            # Exponential race gives weighted sampling without replacement.
            keys = -np.log(np.maximum(rng.random(len(cids)), 1e-12)) / vals
            order = np.argsort(keys)
            return [cids[int(idx)] for idx in order]

        best_score = score(best_perm)
        start = time.time()
        while time.time() - start < time_limit_s:
            iterations += 1
            ants: list[list[int]] = []
            for _ in range(ants_per_iter):
                ants.append(weighted_permutation())
            for perm in ants:
                sc = score(perm)
                if sc < best_score:
                    best_perm, best_score = perm, sc
                    improvements += 1
                for c in perm:
                    pher[c] = 0.95 * pher[c] + 0.05 * (1.0 / (1.0 + sc))
            for c in pher:
                pher[c] = max(1e-6, pher[c] * 0.995)
        return RoutePlan(
            routes=split_by_capacity(best_perm, instance.customers, instance.vehicle_capacity),
            meta={
                "iterations": iterations,
                "improvements": improvements,
                "ants_per_iter": ants_per_iter,
                "best_score": float(best_score),
            },
        )
