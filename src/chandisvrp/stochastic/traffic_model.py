from __future__ import annotations

import math


def peak_intensity(hour: float, peak_hours: list[float], sigma_h: float) -> float:
    return sum(math.exp(-0.5 * ((hour - p) / sigma_h) ** 2) for p in peak_hours)


def congestion_delay_s(base_time_s: float, distance_m: float, hour: float, cfg: dict) -> float:
    intensity = peak_intensity(hour, cfg["peak_hours"], float(cfg["peak_sigma_h"]))
    dist_scale = 1.0 - math.exp(-distance_m / float(cfg["distance_lambda_m"]))
    return base_time_s * float(cfg["congestion_strength"]) * intensity * dist_scale
