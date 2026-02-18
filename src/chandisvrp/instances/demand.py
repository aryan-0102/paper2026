from __future__ import annotations

import numpy as np


def sample_demand(rng: np.random.Generator, lam: float, min_v: int, max_v: int) -> int:
    return int(np.clip(rng.poisson(lam=lam), min_v, max_v))
