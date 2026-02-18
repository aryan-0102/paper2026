from __future__ import annotations

import numpy as np

from chandisvrp.stochastic.traffic_model import peak_intensity


def lognormal_multiplier(rng: np.random.Generator, hour: float, cfg: dict) -> float:
    peak = peak_intensity(hour, cfg["peak_hours"], float(cfg["peak_sigma_h"]))
    ln_cfg = cfg["lognormal"]
    mu = float(ln_cfg["base_mu"]) + float(ln_cfg["peak_mu"]) * peak
    sigma = float(ln_cfg["base_sigma"]) + float(ln_cfg["peak_sigma"]) * peak
    return float(rng.lognormal(mean=mu, sigma=sigma))
