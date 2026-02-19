from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _apply_style() -> None:
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except Exception:
        plt.style.use("ggplot")
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _palette() -> list[str]:
    return ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#8c564b", "#17becf"]


def _annotate_bars(ax: plt.Axes, fmt: str = "{:.2f}") -> None:
    for bar in ax.patches:
        height = bar.get_height()
        ax.annotate(
            fmt.format(height),
            (bar.get_x() + bar.get_width() / 2, height),
            ha="center",
            va="bottom",
            fontsize=8,
            xytext=(0, 3),
            textcoords="offset points",
        )


def make_plots(results: pd.DataFrame, summary: pd.DataFrame, out_dir: str | Path) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, Path] = {}
    _apply_style()
    colors = _palette()

    plt.figure(figsize=(7.4, 4.6))
    axes = results.boxplot(
        column="realized_cost_mean",
        by="solver",
        grid=False,
        showfliers=False,
        patch_artist=True,
        return_type="dict",
    )
    for i, box in enumerate(axes["realized_cost_mean"]["boxes"]):
        box.set_facecolor(colors[i % len(colors)])
        box.set_alpha(0.55)
    plt.title("Cost distribution by solver")
    plt.suptitle("")
    plt.ylabel("Realized cost")
    p1 = out / "cost_distribution.png"
    plt.tight_layout()
    plt.savefig(p1)
    plt.close()
    artifacts["cost_distribution"] = p1

    plt.figure(figsize=(7.4, 4.6))
    feas = summary.groupby("solver")["feasibility_rate"].mean().sort_values()
    ax = feas.plot(kind="bar", color=colors[: len(feas)])
    plt.title("Feasibility rate by solver")
    plt.ylabel("Feasibility rate")
    plt.ylim(0, 1.05)
    _annotate_bars(ax, fmt="{:.2f}")
    p2 = out / "feasibility_bar.png"
    plt.tight_layout()
    plt.savefig(p2)
    plt.close()
    artifacts["feasibility"] = p2

    plt.figure(figsize=(7.4, 4.6))
    robust = summary.groupby("solver")["realized_cost_std"].mean().sort_values()
    ax = robust.plot(kind="bar", color=colors[: len(robust)])
    plt.title("Robustness (lower is better)")
    plt.ylabel("Cost std")
    _annotate_bars(ax, fmt="{:.1f}")
    p3 = out / "robustness_bar.png"
    plt.tight_layout()
    plt.savefig(p3)
    plt.close()
    artifacts["robustness"] = p3

    plt.figure(figsize=(7.4, 4.6))
    solver_means = summary.groupby("solver", as_index=True).agg(
        realized_cost_mean=("realized_cost_mean", "mean"),
        solve_time_s=("solve_time_s", "mean"),
    )
    best_cost = solver_means["realized_cost_mean"].min()
    gap = ((solver_means["realized_cost_mean"] / best_cost) - 1.0) * 100.0
    gap = gap.sort_values()
    ax = gap.plot(kind="bar", color=colors[: len(gap)])
    plt.title("Cost gap vs best solver")
    plt.ylabel("Gap (%)")
    _annotate_bars(ax, fmt="{:.1f}%")
    p_gap = out / "cost_gap_bar.png"
    plt.tight_layout()
    plt.savefig(p_gap)
    plt.close()
    artifacts["cost_gap"] = p_gap

    plt.figure(figsize=(7.4, 4.6))
    for i, (solver, row) in enumerate(solver_means.iterrows()):
        plt.scatter(row["solve_time_s"], row["realized_cost_mean"], color=colors[i % len(colors)], s=60)
        plt.text(
            row["solve_time_s"],
            row["realized_cost_mean"],
            f" {solver}",
            fontsize=8,
            va="center",
        )
    plt.title("Average cost vs solve time")
    plt.xlabel("Solve time (s)")
    plt.ylabel("Realized cost")
    p_scatter = out / "cost_vs_time_scatter.png"
    plt.tight_layout()
    plt.savefig(p_scatter)
    plt.close()
    artifacts["cost_vs_time"] = p_scatter

    plt.figure(figsize=(7.4, 4.6))
    cost_vs_size = (
        summary.groupby(["n_customers", "solver"])["realized_cost_mean"].mean().unstack(fill_value=0)
    )
    ax = cost_vs_size.plot(ax=plt.gca(), marker="o", linewidth=2)
    plt.title("Cost vs problem size")
    plt.xlabel("n_customers")
    plt.ylabel("Realized cost")
    plt.legend(title="solver", frameon=False)
    p4 = out / "cost_vs_size.png"
    plt.tight_layout()
    plt.savefig(p4)
    plt.close()
    artifacts["cost_vs_size"] = p4

    plt.figure(figsize=(7.4, 4.6))
    feas_vs_size = (
        summary.groupby(["n_customers", "solver"])["feasibility_rate"].mean().unstack(fill_value=0)
    )
    ax = feas_vs_size.plot(ax=plt.gca(), marker="o", linewidth=2)
    plt.title("Feasibility vs problem size")
    plt.xlabel("n_customers")
    plt.ylabel("Feasibility rate")
    plt.ylim(0, 1.05)
    plt.legend(title="solver", frameon=False)
    p5 = out / "feasibility_vs_size.png"
    plt.tight_layout()
    plt.savefig(p5)
    plt.close()
    artifacts["feasibility_vs_size"] = p5

    plt.figure(figsize=(7.4, 4.6))
    cost_per_delivery = (
        summary.groupby(["n_customers", "solver"])["cost_per_delivery"].mean().unstack(fill_value=0)
    )
    ax = cost_per_delivery.plot(ax=plt.gca(), marker="o", linewidth=2)
    plt.title("Cost per delivery vs problem size")
    plt.xlabel("n_customers")
    plt.ylabel("Cost per delivery")
    plt.legend(title="solver", frameon=False)
    p6 = out / "cost_per_delivery_vs_size.png"
    plt.tight_layout()
    plt.savefig(p6)
    plt.close()
    artifacts["cost_per_delivery_vs_size"] = p6

    return artifacts
