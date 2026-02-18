from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Customer:
    customer_id: int
    node: int
    demand: int
    service_time_s: float
    tw_start_s: float
    tw_end_s: float
    kind: str


@dataclass
class Instance:
    schema_version: str
    instance_id: str
    city: str
    depot_node: int
    customers: list[Customer]
    n_vehicles: int
    vehicle_capacity: int


@dataclass
class RoutePlan:
    routes: list[list[int]]
    planned_cost: float = 0.0
    planned_distance_m: float = 0.0
    planned_time_s: float = 0.0
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationOutcome:
    total_time_s: float
    total_cost: float
    total_distance_m: float
    feasible: bool
    late_stops: int
    lateness_values_s: list[float]
