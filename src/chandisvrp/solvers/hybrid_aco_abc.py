from __future__ import annotations

import networkx as nx
import numpy as np

from chandisvrp.solvers.abc_solver import ABCSolver
from chandisvrp.solvers.aco_solver import ACOSolver
from chandisvrp.solvers.base import Solver
from chandisvrp.types import Instance, RoutePlan


class HybridACOABCSolver(Solver):
    name = "hybrid_aco_abc"

    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        aco_plan = ACOSolver().solve(g, instance, rng, time_limit_s * 0.5)
        flat = [cid for r in aco_plan.routes for cid in r]
        tmp_instance = Instance(
            schema_version=instance.schema_version,
            instance_id=instance.instance_id,
            city=instance.city,
            depot_node=instance.depot_node,
            customers=sorted(instance.customers, key=lambda c: flat.index(c.customer_id) if c.customer_id in flat else 10**9),
            n_vehicles=instance.n_vehicles,
            vehicle_capacity=instance.vehicle_capacity,
        )
        return ABCSolver().solve(g, tmp_instance, rng, time_limit_s * 0.5)
