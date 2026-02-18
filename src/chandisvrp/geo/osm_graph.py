from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx

logger = logging.getLogger(__name__)


def _annotate_graph(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    for _, _, _, data in g.edges(keys=True, data=True):
        length = float(data.get("length", 500.0))
        speed_kph = float(data.get("speed_kph", 30.0))
        data["length_m"] = length
        data["base_speed_kph"] = speed_kph
        data["base_time_s"] = max(1.0, length / (speed_kph * 1000 / 3600))
    return g


def build_synthetic_graph(grid_w: int = 8, grid_h: int = 8, spacing_m: float = 500.0) -> nx.MultiDiGraph:
    g_simple = nx.grid_2d_graph(grid_w, grid_h)
    mapping = {node: i for i, node in enumerate(g_simple.nodes())}
    g_simple = nx.relabel_nodes(g_simple, mapping)
    mg = nx.MultiDiGraph()
    for n in g_simple.nodes:
        x = (n % grid_w) * spacing_m
        y = (n // grid_w) * spacing_m
        mg.add_node(n, x=x, y=y)
    for u, v in g_simple.edges:
        mg.add_edge(u, v, length=spacing_m, speed_kph=32)
        mg.add_edge(v, u, length=spacing_m, speed_kph=32)
    return _annotate_graph(mg)


def load_or_build_graph(place: str, path: str | Path, use_osm: bool = True, synthetic_cfg: dict | None = None) -> nx.MultiDiGraph:
    target = Path(path)
    if target.exists():
        try:
            import osmnx as ox

            g = ox.load_graphml(target)
            return _annotate_graph(g)
        except Exception:
            logger.exception("Failed reading graphml; fallback synthetic")
    if use_osm:
        try:
            import osmnx as ox

            logger.info("Downloading OSM graph for %s", place)
            g = ox.graph_from_place(place, network_type="drive")
            g = _annotate_graph(g)
            target.parent.mkdir(parents=True, exist_ok=True)
            ox.save_graphml(g, target)
            return g
        except Exception:
            logger.exception("OSM download failed; using synthetic fallback")
    cfg = synthetic_cfg or {}
    return build_synthetic_graph(
        grid_w=int(cfg.get("grid_w", 8)),
        grid_h=int(cfg.get("grid_h", 8)),
        spacing_m=float(cfg.get("spacing_m", 500.0)),
    )
