from __future__ import annotations

from chandisvrp.types import Customer


def split_by_capacity(permutation: list[int], customers: list[Customer], capacity: int) -> list[list[int]]:
    cmap = {c.customer_id: c for c in customers}
    routes: list[list[int]] = []
    cur: list[int] = []
    load = 0
    for cid in permutation:
        dem = cmap[cid].demand
        if cur and load + dem > capacity:
            routes.append(cur)
            cur = []
            load = 0
        cur.append(cid)
        load += dem
    if cur:
        routes.append(cur)
    return routes
