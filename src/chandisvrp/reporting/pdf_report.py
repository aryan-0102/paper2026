from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from chandisvrp.reporting.plots import make_plots


def _draw_lines(c: canvas.Canvas, lines: list[str], x: float, y: float, h: float) -> float:
    for line in lines:
        c.drawString(x, y, line)
        y -= 12
        if y < 90:
            c.showPage()
            y = h - 40
    return y


def generate_pdf_report(results_csv: str | Path, summary_csv: str | Path, out_pdf: str | Path) -> None:
    results = pd.read_csv(results_csv).sort_values(["instance_id", "solver", "run_seed"])
    summary = pd.read_csv(summary_csv).sort_values(["instance_id", "solver"])
    plots = make_plots(results, summary, Path(out_pdf).parent / "_figures")

    c = canvas.Canvas(str(out_pdf), pagesize=A4)
    w, h = A4
    c.setTitle("ChandiSVRPBench Report")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h - 40, "ChandiSVRPBench: Benchmark Report")
    c.setFont("Helvetica", 10)
    top = h - 70
    n_instances = summary["instance_id"].nunique()
    n_solvers = summary["solver"].nunique()
    n_runs = results["run_seed"].nunique()
    n_customers = summary["n_customers"]
    size_span = f"{int(n_customers.min())}-{int(n_customers.max())}" if not n_customers.empty else "n/a"
    c.drawString(40, top, f"Instances: {n_instances} | Solvers: {n_solvers} | Runs: {n_runs} | Customers: {size_span}")

    solver_stats = summary.groupby("solver", as_index=True).agg(
        realized_cost_mean=("realized_cost_mean", "mean"),
        feasibility_rate=("feasibility_rate", "mean"),
        realized_cost_std=("realized_cost_std", "mean"),
        solve_time_s=("solve_time_s", "mean"),
        cvr_mean=("cvr_mean", "mean"),
        cost_per_delivery=("cost_per_delivery", "mean"),
    )
    best_cost_val = solver_stats["realized_cost_mean"].min()
    solver_stats["cost_gap_pct"] = (solver_stats["realized_cost_mean"] / best_cost_val - 1.0) * 100.0
    best_cost = solver_stats["realized_cost_mean"].idxmin()
    best_feas = solver_stats["feasibility_rate"].idxmax()
    fastest = solver_stats["solve_time_s"].idxmin()
    most_robust = solver_stats["realized_cost_std"].idxmin()

    y = top - 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Highlights")
    c.setFont("Helvetica", 10)
    y -= 16
    y = _draw_lines(
        c,
        [
            f"Best cost: {best_cost} ({solver_stats.loc[best_cost, 'realized_cost_mean']:.1f})",
            f"Best feasibility: {best_feas} ({solver_stats.loc[best_feas, 'feasibility_rate']:.2f})",
            f"Most robust: {most_robust} (std {solver_stats.loc[most_robust, 'realized_cost_std']:.1f})",
            f"Fastest solver: {fastest} ({solver_stats.loc[fastest, 'solve_time_s']:.2f}s)",
        ],
        40,
        y,
        h,
    )

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 4, "Solver averages")
    c.setFont("Helvetica", 10)
    y -= 20
    header = f"{'solver':<12} {'cost':>10} {'gap%':>7} {'feas':>6} {'std':>9} {'time_s':>8} {'cvr':>7} {'cpd':>7}"
    y = _draw_lines(c, [header], 40, y, h)
    rows = []
    for solver, row in solver_stats.sort_values("realized_cost_mean").iterrows():
        rows.append(
            f"{solver:<12} {row['realized_cost_mean']:>10.1f} {row['cost_gap_pct']:>7.1f}"
            f" {row['feasibility_rate']:>6.2f} {row['realized_cost_std']:>9.1f} {row['solve_time_s']:>8.2f}"
            f" {row['cvr_mean']:>7.3f} {row['cost_per_delivery']:>7.2f}"
        )
    y = _draw_lines(c, rows, 40, y, h)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 4, "Per-instance snapshot (first 10 rows)")
    c.setFont("Helvetica", 10)
    y -= 20
    cols = ["instance_id", "solver", "realized_cost_mean", "feasibility_rate", "cvr_mean"]
    lines = [
        f"{row['instance_id']:<18} {row['solver']:<10} cost={row['realized_cost_mean']:.1f}"
        f" feas={row['feasibility_rate']:.2f} cvr={row['cvr_mean']:.3f}"
        for _, row in summary[cols].head(10).iterrows()
    ]
    _draw_lines(c, lines, 40, y, h)

    for title, path in sorted(plots.items()):
        c.showPage()
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, h - 40, title.replace("_", " ").title())
        img = ImageReader(str(path))
        c.drawImage(img, 40, 120, width=w - 80, height=h - 180, preserveAspectRatio=True, anchor="c")

    c.save()
