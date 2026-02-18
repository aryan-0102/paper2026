from __future__ import annotations

import numpy as np

from chandisvrp.stochastic.accidents import accident_delay_s
from chandisvrp.stochastic.delay_model import lognormal_multiplier
from chandisvrp.stochastic.traffic_model import congestion_delay_s


def travel_time_s(
    rng: np.random.Generator,
    base_time_s: float,
    distance_m: float,
    depart_time_s: float,
    cfg: dict,
) -> float:
    hour = (depart_time_s / 3600.0) % 24.0
    c_delay = congestion_delay_s(base_time_s, distance_m, hour, cfg)
    mult = lognormal_multiplier(rng, hour, cfg)
    a_delay = accident_delay_s(rng, cfg)
    return max(1.0, (base_time_s + c_delay) * mult + a_delay)
