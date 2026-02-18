from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np

from chandisvrp.instances.demand import sample_demand
from chandisvrp.instances.time_windows import sample_time_window
from chandisvrp.types import Customer, Instance


def build_instances(g: nx.MultiDiGraph, cfg: dict[str, Any], city: str, rng: np.random.Generator) -> list[Instance]:
    inst_cfg = cfg["instance"]
    depot = int(sorted(g.nodes())[0])
    nodes = [int(n) for n in g.nodes() if int(n) != depot]
    instances: list[Instance] = []
    for i in range(int(inst_cfg["n_instances"])):
        n_customers = int(inst_cfg["n_customers"][i % len(inst_cfg["n_customers"])])
        chosen = rng.choice(nodes, size=n_customers, replace=False)
        customers: list[Customer] = []
        for cid, node in enumerate(chosen, start=1):
            kind = "residential" if rng.random() < float(inst_cfg["customer_types"]["residential_prob"]) else "commercial"
            tw_s, tw_e = sample_time_window(rng, kind)
            demand = sample_demand(
                rng,
                float(inst_cfg["demand"]["lambda"]),
                int(inst_cfg["demand"]["min"]),
                int(inst_cfg["demand"]["max"]),
            )
            service = float(rng.integers(inst_cfg["service_time_s"]["min"], inst_cfg["service_time_s"]["max"] + 1))
            customers.append(Customer(cid, int(node), demand, service, tw_s, tw_e, kind))
        instances.append(
            Instance(
                schema_version="1.0",
                instance_id=f"{city.lower()}_{n_customers}_{i}",
                city=city,
                depot_node=depot,
                customers=customers,
                n_vehicles=int(inst_cfg["n_vehicles"]),
                vehicle_capacity=int(inst_cfg["vehicle_capacity"]),
            )
        )
    return instances
