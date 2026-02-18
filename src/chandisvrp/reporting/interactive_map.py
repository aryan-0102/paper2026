from __future__ import annotations

import webbrowser
from pathlib import Path

import networkx as nx

from chandisvrp.types import Instance, RoutePlan


def _latlon_from_xy(x: float, y: float) -> tuple[float, float]:
    # synthetic fallback coordinates are meters; map them to a tiny lat/lon tile around Chandigarh
    base_lat, base_lon = 30.7333, 76.7794
    return base_lat + (y / 111_000.0), base_lon + (x / (111_000.0 * 0.86))


def generate_route_map(
    g: nx.MultiDiGraph,
    instance: Instance,
    plan: RoutePlan,
    out_html: str | Path,
    open_browser: bool = True,
) -> Path:
    try:
        import folium
    except Exception as exc:  # pragma: no cover - dependency runtime check
        raise RuntimeError("folium is required for interactive map generation") from exc

    depot = g.nodes[instance.depot_node]
    c_lat, c_lon = _latlon_from_xy(float(depot.get("x", 0.0)), float(depot.get("y", 0.0)))
    m = folium.Map(location=[c_lat, c_lon], zoom_start=12, control_scale=True)

    cmap = {c.customer_id: c for c in instance.customers}
    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "beige",
        "darkblue",
        "darkgreen",
    ]

    folium.Marker([c_lat, c_lon], popup="Depot", icon=folium.Icon(color="black", icon="home")).add_to(m)

    for idx, route in enumerate(plan.routes):
        color = colors[idx % len(colors)]
        poly: list[tuple[float, float]] = [(c_lat, c_lon)]
        for cid in route:
            customer = cmap[cid]
            nd = g.nodes[customer.node]
            lat, lon = _latlon_from_xy(float(nd.get("x", 0.0)), float(nd.get("y", 0.0)))
            poly.append((lat, lon))
            folium.CircleMarker(
                [lat, lon],
                radius=4,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=f"C{cid} | {customer.kind} | demand={customer.demand}",
            ).add_to(m)
        poly.append((c_lat, c_lon))
        folium.PolyLine(poly, color=color, weight=3, opacity=0.8, tooltip=f"Route {idx + 1}").add_to(m)

    out = Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out))
    if open_browser:
        webbrowser.open_new_tab(out.resolve().as_uri())
    return out
