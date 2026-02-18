from __future__ import annotations

import numpy as np


def cvr(values: list[float]) -> float:
    arr = np.array(values, dtype=float)
    if arr.mean() == 0:
        return 0.0
    return float(arr.std(ddof=0) / arr.mean())
