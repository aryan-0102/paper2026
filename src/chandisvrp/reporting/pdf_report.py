from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from chandisvrp.reporting.plots import make_plots


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
    c.drawString(40, top, "Executive summary (first 15 rows)")
    y = top - 20
    cols = ["instance_id", "solver", "realized_cost_mean", "feasibility_rate", "cvr_mean"]
    for _, row in summary[cols].head(15).iterrows():
        c.drawString(40, y, f"{row['instance_id']:<18} {row['solver']:<14} cost={row['realized_cost_mean']:.1f} feas={row['feasibility_rate']:.2f} cvr={row['cvr_mean']:.3f}")
        y -= 12
        if y < 100:
            c.showPage(); y = h - 40

    for title, path in sorted(plots.items()):
        c.showPage()
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, h - 40, title.replace("_", " ").title())
        img = ImageReader(str(path))
        c.drawImage(img, 40, 120, width=w - 80, height=h - 180, preserveAspectRatio=True, anchor="c")

    c.save()
