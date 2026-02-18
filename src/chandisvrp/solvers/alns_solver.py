from __future__ import annotations

import copy
import math
import time

import networkx as nx
import numpy as np

from chandisvrp.solvers.base import Solver
from chandisvrp.solvers.constructive import NearestNeighbor2OptSolver, route_length
from chandisvrp.solvers.operators_destroy import random_destroy
from chandisvrp.solvers.operators_repair import greedy_repair
from chandisvrp.solvers.split import split_by_capacity
from chandisvrp.types import Instance, RoutePlan


class ALNSSolver(Solver):
    name = "alns"

    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        seed_plan = NearestNeighbor2OptSolver().solve(g, instance, rng, 1)
        node_of = {c.customer_id: c.node for c in instance.customers}

        def score(routes: list[list[int]]) -> float:
            cap_pen = 0.0
            cmap = {c.customer_id: c for c in instance.customers}
            for r in routes:
                load = sum(cmap[c].demand for c in r)
                cap_pen += max(0, load - instance.vehicle_capacity) * 1e5
            return sum(route_length(r, g, node_of, instance.depot_node) for r in routes) + cap_pen

        curr = copy.deepcopy(seed_plan.routes)
        best = copy.deepcopy(curr)
        curr_s = best_s = score(curr)
        temp = 100.0
        start = time.time()
        while time.time() - start < time_limit_s:
            destroyed, removed = random_destroy(curr, rng)
            repaired = greedy_repair(destroyed, removed, rng)
            cand_flat = [c for r in repaired for c in r]
            repaired = split_by_capacity(cand_flat, instance.customers, instance.vehicle_capacity)
            cand_s = score(repaired)
            if cand_s < curr_s or rng.random() < math.exp((curr_s - cand_s) / max(1e-6, temp)):
                curr, curr_s = repaired, cand_s
            if cand_s < best_s:
                best, best_s = repaired, cand_s
            temp *= 0.995
        return RoutePlan(routes=best)
