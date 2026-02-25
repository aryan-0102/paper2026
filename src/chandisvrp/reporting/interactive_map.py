from __future__ import annotations

import webbrowser
from pathlib import Path

import networkx as nx
from branca.element import MacroElement, Template

from chandisvrp.types import Instance, RoutePlan


def _latlon_from_xy(x: float, y: float) -> tuple[float, float]:
    # If coordinates look like lat/lon (e.g. Chandigarh is ~30, ~76), use them directly.
    # Synthetic fallback coordinates are meters from (0,0).
    if -90 <= y <= 90 and -180 <= x <= 180:
        return y, x
    base_lat, base_lon = 30.733433, 76.779710
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

    all_customers = folium.FeatureGroup(name="All customers", show=True)
    for customer in instance.customers:
        nd = g.nodes[customer.node]
        lat, lon = _latlon_from_xy(float(nd.get("x", 0.0)), float(nd.get("y", 0.0)))
        folium.CircleMarker(
            [lat, lon],
            radius=2,
            color="#555555",
            fill=True,
            fill_opacity=0.6,
        ).add_to(all_customers)
    all_customers.add_to(m)

    for idx, route in enumerate(plan.routes):
        color = colors[idx % len(colors)]
        route_nodes = [instance.depot_node]
        for cid in route:
            customer = cmap[cid]
            route_nodes.append(customer.node)
        route_nodes.append(instance.depot_node)

        full_path_coords: list[tuple[float, float]] = []
        for i in range(len(route_nodes) - 1):
            u, v = route_nodes[i], route_nodes[i + 1]
            try:
                # Get shortest path in the graph
                path = nx.shortest_path(g, u, v, weight="length")
                for node in path[:-1]:  # Exclude last node to avoid duplicates
                    nd = g.nodes[node]
                    full_path_coords.append(_latlon_from_xy(float(nd.get("x", 0.0)), float(nd.get("y", 0.0))))
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # Fallback to direct line if no path exists
                u_nd = g.nodes[u]
                full_path_coords.append(_latlon_from_xy(float(u_nd.get("x", 0.0)), float(u_nd.get("y", 0.0))))

        # Add the very last node coordinate
        last_nd = g.nodes[route_nodes[-1]]
        full_path_coords.append(_latlon_from_xy(float(last_nd.get("x", 0.0)), float(last_nd.get("y", 0.0))))

        # Draw the Hamiltonian path
        folium.PolyLine(full_path_coords, color=color, weight=3, opacity=0.8, tooltip=f"Route {idx + 1}").add_to(m)

        # Draw markers for customers (already in original code, but we moved the PolyLine logic)
        for cid in route:
            customer = cmap[cid]
            nd = g.nodes[customer.node]
            lat, lon = _latlon_from_xy(float(nd.get("x", 0.0)), float(nd.get("y", 0.0)))
            folium.CircleMarker(
                [lat, lon],
                radius=4,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=f"C{cid} | {customer.kind} | demand={customer.demand}",
            ).add_to(m)
            # Add permanent label for each customer
            folium.Marker(
                [lat, lon],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 8pt; color: black; font-weight: bold;">{cid}</div>',
                    icon_anchor=(0, 0),
                )
            ).add_to(m)

    folium.LayerControl().add_to(m)

    legend_items = ""
    for idx in range(min(len(plan.routes), len(colors))):
        legend_items += (
            f'<li><span style="display:inline-block;width:12px;height:12px;'
            f'background:{colors[idx]};margin-right:6px;"></span>Route {idx + 1}</li>'
        )
    legend_items += '<li><span style="display:inline-block;width:12px;height:12px;background:black;margin-right:6px;"></span>Depot</li>'
    legend_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="position: fixed; bottom: 60px; left: 8px; z-index: 9999; background: white; padding: 8px 12px; border-radius: 6px; box-shadow: 0 0 8px rgba(0,0,0,0.2); font-size: 11px;">
        <strong>Legend</strong>
        <ul style="list-style:none;margin:4px 0 0;padding:0;">
            {legend_items}
        </ul>
    </div>
    {{% endmacro %}}
    """
    legend = MacroElement()
    legend._template = Template(legend_html)
    m.get_root().add_child(legend)

    out = Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out))
    if open_browser:
        webbrowser.open_new_tab(out.resolve().as_uri())
    return out
