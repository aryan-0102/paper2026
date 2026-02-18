from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def make_plots(results: pd.DataFrame, summary: pd.DataFrame, out_dir: str | Path) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, Path] = {}

    plt.figure(figsize=(7, 4))
    results.boxplot(column="realized_cost_mean", by="solver", grid=False)
    plt.title("Cost distribution by solver")
    plt.suptitle("")
    p1 = out / "cost_distribution.png"
    plt.tight_layout(); plt.savefig(p1); plt.close()
    artifacts["cost_distribution"] = p1

    plt.figure(figsize=(7, 4))
    summary.groupby("solver")["feasibility_rate"].mean().sort_values().plot(kind="bar")
    plt.title("Feasibility rate")
    p2 = out / "feasibility_bar.png"
    plt.tight_layout(); plt.savefig(p2); plt.close()
    artifacts["feasibility"] = p2

    plt.figure(figsize=(7, 4))
    summary.groupby("solver")["realized_cost_std"].mean().sort_values().plot(kind="bar")
    plt.title("Robustness (cost std)")
    p3 = out / "robustness_bar.png"
    plt.tight_layout(); plt.savefig(p3); plt.close()
    artifacts["robustness"] = p3

    plt.figure(figsize=(7, 4))
    summary.groupby(["n_customers", "solver"])["realized_cost_mean"].mean().unstack(fill_value=0).plot(ax=plt.gca())
    plt.title("Cost vs size")
    plt.xlabel("n_customers")
    p4 = out / "cost_vs_size.png"
    plt.tight_layout(); plt.savefig(p4); plt.close()
    artifacts["cost_vs_size"] = p4

    return artifacts
