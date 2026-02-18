from __future__ import annotations

import numpy as np


def accident_delay_s(rng: np.random.Generator, cfg: dict) -> float:
    ac = cfg["accidents"]
    if rng.random() < float(ac["prob_per_leg"]):
        return max(0.0, float(rng.normal(float(ac["delay_mean_s"]), float(ac["delay_std_s"]))))
    return 0.0
