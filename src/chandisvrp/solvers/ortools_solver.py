from __future__ import annotations

import networkx as nx
import numpy as np

from chandisvrp.solvers.constructive import NearestNeighbor2OptSolver
from chandisvrp.solvers.base import Solver
from chandisvrp.types import Instance, RoutePlan


class OrtoolsSolver(Solver):
    name = "ortools"

    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        try:
            from ortools.constraint_solver import pywrapcp, routing_enums_pb2
        except Exception:
            return NearestNeighbor2OptSolver().solve(g, instance, rng, time_limit_s)

        n = len(instance.customers)
        nodes = [instance.depot_node] + [c.node for c in instance.customers]
        demands = [0] + [c.demand for c in instance.customers]

        manager = pywrapcp.RoutingIndexManager(n + 1, instance.n_vehicles, 0)
        routing = pywrapcp.RoutingModel(manager)

        def dist_cb(i: int, j: int) -> int:
            ni, nj = nodes[manager.IndexToNode(i)], nodes[manager.IndexToNode(j)]
            if g.has_edge(ni, nj):
                data = next(iter(g.get_edge_data(ni, nj).values()))
                return int(data.get("length_m", data.get("length", 500)))
            return 1000

        dist_idx = routing.RegisterTransitCallback(dist_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(dist_idx)

        def demand_cb(i: int) -> int:
            return int(demands[manager.IndexToNode(i)])

        demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
        routing.AddDimensionWithVehicleCapacity(demand_idx, 0, [instance.vehicle_capacity] * instance.n_vehicles, True, "Capacity")

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.time_limit.seconds = max(1, int(time_limit_s))
        solution = routing.SolveWithParameters(params)
        if solution is None:
            return NearestNeighbor2OptSolver().solve(g, instance, rng, time_limit_s)

        routes: list[list[int]] = []
        for v in range(instance.n_vehicles):
            idx = routing.Start(v)
            route: list[int] = []
            while not routing.IsEnd(idx):
                node = manager.IndexToNode(idx)
                if node != 0:
                    route.append(node)
                idx = solution.Value(routing.NextVar(idx))
            if route:
                routes.append(route)
        mapped = [[instance.customers[i - 1].customer_id for i in r] for r in routes]
        return RoutePlan(routes=mapped)
