from __future__ import annotations

from pathlib import Path

import typer

from chandisvrp.config import load_config
from chandisvrp.evaluation.runner import BenchmarkRunner
from chandisvrp.geo.osm_graph import load_or_build_graph
from chandisvrp.instances.generator import build_instances
from chandisvrp.instances.serialization import save_instance
from chandisvrp.reporting.interactive_map import generate_route_map
from chandisvrp.reporting.pdf_report import generate_pdf_report
from chandisvrp.utils.seed import set_global_seed

app = typer.Typer(add_completion=False)


@app.command("download-osm")
def download_osm(place: str = "Chandigarh, India", config: str = "configs/default.yaml") -> None:
    cfg = load_config(config)
    g = load_or_build_graph(place, cfg["data"]["graph_path"], use_osm=True, synthetic_cfg=cfg["graph"]["synthetic"])
    typer.echo(f"Graph loaded with {g.number_of_nodes()} nodes")


@app.command("build-instances")
def build_instances_cmd(config: str = "configs/default.yaml") -> None:
    cfg = load_config(config)
    rng = set_global_seed(int(cfg["seed"]))
    g = load_or_build_graph(cfg["place"], cfg["data"]["graph_path"], use_osm=bool(cfg["graph"]["use_osm"]), synthetic_cfg=cfg["graph"]["synthetic"])
    instances = build_instances(g, cfg, cfg["city"], rng)
    out_dir = Path(cfg["data"]["instances_dir"])
    for inst in instances:
        save_instance(inst, out_dir / f"{inst.instance_id}.json")
    typer.echo(f"Saved {len(instances)} instances to {out_dir}")


@app.command("run-benchmark")
def run_benchmark(config: str = "configs/benchmark_small.yaml") -> None:
    cfg = load_config(config)
    g = load_or_build_graph(cfg["place"], cfg["data"]["graph_path"], use_osm=bool(cfg["graph"]["use_osm"]), synthetic_cfg=cfg["graph"]["synthetic"])
    inst_paths = sorted(Path(cfg["data"]["instances_dir"]).glob("*.json"))
    if not inst_paths:
        build_instances_cmd(config)
        inst_paths = sorted(Path(cfg["data"]["instances_dir"]).glob("*.json"))
    runner = BenchmarkRunner(g, cfg)
    df, summary = runner.run(inst_paths)
    runner.save(df, summary)
    typer.echo(f"Saved results to {cfg['data']['results_csv']}")


@app.command("run-all")
def run_all(config: str = "configs/benchmark_small.yaml", map_out: str = "reports/interactive_map.html", open_map: bool = True) -> None:
    cfg = load_config(config)
    rng = set_global_seed(int(cfg["seed"]))
    g = load_or_build_graph(
        cfg["place"],
        cfg["data"]["graph_path"],
        use_osm=bool(cfg["graph"]["use_osm"]),
        synthetic_cfg=cfg["graph"]["synthetic"],
    )
    instances = build_instances(g, cfg, cfg["city"], rng)
    out_dir = Path(cfg["data"]["instances_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    instance_paths = []
    for inst in instances:
        ip = out_dir / f"{inst.instance_id}.json"
        save_instance(inst, ip)
        instance_paths.append(ip)

    runner = BenchmarkRunner(g, cfg)
    df, summary = runner.run(instance_paths)
    runner.save(df, summary)
    generate_pdf_report(cfg["data"]["results_csv"], cfg["data"]["summary_csv"], cfg["data"]["report_pdf"])

    # Build representative map using the best solver from first instance
    first_instance = instances[0]
    subset = summary[summary["instance_id"] == first_instance.instance_id].sort_values("realized_cost_mean")
    best_solver_name = str(subset.iloc[0]["solver"]) if len(subset) else cfg["evaluation"]["solvers"][0]
    from chandisvrp.evaluation.runner import SOLVERS

    best_solver = SOLVERS[best_solver_name]()
    plan = best_solver.solve(g, first_instance, rng, float(cfg["evaluation"]["time_limit_s"]))
    html = generate_route_map(g, first_instance, plan, map_out, open_browser=open_map)

    typer.echo(f"Completed pipeline.\nPDF: {cfg['data']['report_pdf']}\nMap: {html}")


@app.command("make-report")
def make_report(results: str, summary: str, out: str) -> None:
    generate_pdf_report(results, summary, out)
    typer.echo(f"Wrote report to {out}")


if __name__ == "__main__":
    app()
