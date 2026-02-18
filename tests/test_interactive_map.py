from pathlib import Path

from chandisvrp.geo.osm_graph import build_synthetic_graph
from chandisvrp.reporting.interactive_map import generate_route_map
from chandisvrp.types import Customer, Instance, RoutePlan


def test_interactive_map_written(tmp_path: Path) -> None:
    g = build_synthetic_graph(3, 3, 100)
    customers = [
        Customer(1, 1, 1, 60, 0, 50000, "residential"),
        Customer(2, 2, 1, 60, 0, 50000, "commercial"),
    ]
    inst = Instance("1.0", "i-map", "Chandigarh", 0, customers, 1, 10)
    out = generate_route_map(g, inst, RoutePlan([[1, 2]]), tmp_path / "map.html", open_browser=False)
    assert out.exists()
    assert "Leaflet" in out.read_text()
