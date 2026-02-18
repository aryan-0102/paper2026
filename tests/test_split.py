from chandisvrp.solvers.split import split_by_capacity
from chandisvrp.types import Customer


def test_split_capacity_respected() -> None:
    customers = [Customer(i, i, 3, 60, 0, 1000, "residential") for i in range(1, 7)]
    routes = split_by_capacity([1, 2, 3, 4, 5, 6], customers, capacity=7)
    cmap = {c.customer_id: c for c in customers}
    assert all(sum(cmap[c].demand for c in r) <= 7 for r in routes)
