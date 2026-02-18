from __future__ import annotations

import numpy as np


def sample_time_window(rng: np.random.Generator, kind: str) -> tuple[float, float]:
    if kind == "residential":
        start_h = float(rng.uniform(9.0, 12.0))
        width_h = float(rng.uniform(3.0, 6.0))
    else:
        start_h = float(rng.uniform(10.0, 14.0))
        width_h = float(rng.uniform(4.0, 7.0))
    return start_h * 3600, min(24 * 3600.0, (start_h + width_h) * 3600)
