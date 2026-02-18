from __future__ import annotations

import networkx as nx
import numpy as np

from chandisvrp.stochastic.travel_time import travel_time_s
from chandisvrp.types import Instance, RoutePlan, SimulationOutcome


def _edge_stats(g: nx.MultiDiGraph, u: int, v: int) -> tuple[float, float]:
    if g.has_edge(u, v):
        data = next(iter(g.get_edge_data(u, v).values()))
        return float(data.get("length_m", data.get("length", 500.0))), float(data.get("base_time_s", 60.0))
    return 500.0, 60.0


def simulate_plan(
    g: nx.MultiDiGraph,
    instance: Instance,
    plan: RoutePlan,
    stochastic_cfg: dict,
    rng: np.random.Generator,
) -> SimulationOutcome:
    c_map = {c.customer_id: c for c in instance.customers}
    total_time = 0.0
    total_dist = 0.0
    late = 0
    lateness: list[float] = []
    for route in plan.routes:
        t = 8 * 3600.0
        prev = instance.depot_node
        for cid in route:
            c = c_map[cid]
            d, bt = _edge_stats(g, prev, c.node)
            tr_t = travel_time_s(rng, bt, d, t, stochastic_cfg)
            t += tr_t
            total_dist += d
            if t < c.tw_start_s:
                t = c.tw_start_s
            if t > c.tw_end_s:
                late += 1
                lateness.append(t - c.tw_end_s)
            t += c.service_time_s
            prev = c.node
        d, bt = _edge_stats(g, prev, instance.depot_node)
        tr_t = travel_time_s(rng, bt, d, t, stochastic_cfg)
        t += tr_t
        total_dist += d
        total_time += t - 8 * 3600.0
    feasible = late == 0
    return SimulationOutcome(
        total_time_s=total_time,
        total_cost=total_dist + 0.1 * total_time,
        total_distance_m=total_dist,
        feasible=feasible,
        late_stops=late,
        lateness_values_s=lateness,
    )
