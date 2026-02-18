import numpy as np

from chandisvrp.geo.osm_graph import build_synthetic_graph
from chandisvrp.stochastic.simulator import simulate_plan
from chandisvrp.types import Customer, Instance, RoutePlan


def test_simulator_returns_outcome() -> None:
    g = build_synthetic_graph(4, 4, 200)
    customers = [
        Customer(1, 1, 2, 60, 9 * 3600, 15 * 3600, "residential"),
        Customer(2, 2, 3, 90, 9 * 3600, 18 * 3600, "commercial"),
    ]
    inst = Instance("1.0", "i1", "Chandigarh", 0, customers, 2, 10)
    out = simulate_plan(
        g,
        inst,
        RoutePlan([[1, 2]]),
        {
            "peak_hours": [8.0, 17.0],
            "peak_sigma_h": 1.5,
            "congestion_strength": 0.3,
            "distance_lambda_m": 2500,
            "lognormal": {"base_mu": 0.0, "peak_mu": 0.1, "base_sigma": 0.1, "peak_sigma": 0.2},
            "accidents": {"prob_per_leg": 0.0, "delay_mean_s": 100, "delay_std_s": 10},
        },
        np.random.default_rng(0),
    )
    assert out.total_time_s > 0
    assert out.total_distance_m > 0
