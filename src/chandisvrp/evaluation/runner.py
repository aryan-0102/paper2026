from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

from chandisvrp.evaluation.io import write_metadata, write_results
from chandisvrp.evaluation.metrics import cvr
from chandisvrp.instances.serialization import load_instance
from chandisvrp.solvers.abc_solver import ABCSolver
from chandisvrp.solvers.aco_solver import ACOSolver
from chandisvrp.solvers.alns_solver import ALNSSolver
from chandisvrp.solvers.constructive import NearestNeighbor2OptSolver, NearestNeighborSolver, RandomSolver
from chandisvrp.solvers.hybrid_aco_abc import HybridACOABCSolver
from chandisvrp.solvers.ortools_solver import OrtoolsSolver
from chandisvrp.stochastic.simulator import simulate_plan


SOLVERS = {
    "nn2opt": NearestNeighbor2OptSolver,
    "nearest_neighbor": NearestNeighborSolver,
    "random": RandomSolver,
    "ortools": OrtoolsSolver,
    "abc": ABCSolver,
    "aco": ACOSolver,
    "hybrid_aco_abc": HybridACOABCSolver,
    "alns": ALNSSolver,
}


class BenchmarkRunner:
    def __init__(self, g: nx.MultiDiGraph, cfg: dict[str, Any]):
        self.g = g
        self.cfg = cfg

    def run(self, instance_paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
        rows = []
        eval_cfg = self.cfg["evaluation"]
        for p in instance_paths:
            instance = load_instance(p)
            for seed in eval_cfg["run_seeds"]:
                for sname in eval_cfg["solvers"]:
                    rng = np.random.default_rng(seed)
                    solver = SOLVERS[sname]()
                    t0 = time.time()
                    plan = solver.solve(self.g, instance, rng, float(eval_cfg["time_limit_s"]))
                    solve_time = time.time() - t0
                    outcomes = [simulate_plan(self.g, instance, plan, self.cfg["stochastic"], np.random.default_rng(seed + i + 999)) for i in range(int(eval_cfg["mc_rollouts"]))]
                    costs = [o.total_cost for o in outcomes]
                    times = [o.total_time_s for o in outcomes]
                    lates = [v for o in outcomes for v in o.lateness_values_s]
                    row = {
                        "instance_id": instance.instance_id,
                        "city": instance.city,
                        "n_customers": len(instance.customers),
                        "stochasticity_level": "default",
                        "solver": sname,
                        "run_seed": seed,
                        "solve_time_s": solve_time,
                        "planned_cost": plan.planned_cost,
                        "planned_distance_m": plan.planned_distance_m,
                        "planned_time_s": plan.planned_time_s,
                        "mc_rollouts": len(outcomes),
                        "realized_cost_mean": float(np.mean(costs)),
                        "realized_cost_std": float(np.std(costs)),
                        "realized_time_mean": float(np.mean(times)),
                        "realized_time_std": float(np.std(times)),
                        "feasibility_rate": float(np.mean([1.0 if o.feasible else 0.0 for o in outcomes])),
                        "cvr_mean": cvr(costs),
                        "cost_per_delivery": float(np.mean(costs)) / max(len(instance.customers), 1),
                        "lateness_mean_s": float(np.mean(lates)) if lates else 0.0,
                        "lateness_p95_s": float(np.percentile(lates, 95)) if lates else 0.0,
                    }
                    rows.append(row)
        df = pd.DataFrame(rows)
        summary = df.groupby(["instance_id", "solver"], as_index=False).mean(numeric_only=True)
        std_metrics = [
            "solve_time_s",
            "realized_cost_mean",
            "realized_time_mean",
            "feasibility_rate",
            "cvr_mean",
            "cost_per_delivery",
            "lateness_mean_s",
        ]
        run_std = (
            df.groupby(["instance_id", "solver"], as_index=False)[std_metrics]
            .std(numeric_only=True)
            .rename(columns={m: f"{m}_run_std" for m in std_metrics})
        )
        summary = summary.merge(run_std, on=["instance_id", "solver"], how="left")
        return df, summary

    def save(self, df: pd.DataFrame, summary: pd.DataFrame) -> None:
        data_cfg = self.cfg["data"]
        write_results(df, data_cfg["results_csv"])
        write_results(summary, data_cfg["summary_csv"])
        write_metadata(
            {
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "config": self.cfg,
                "package_versions": {"numpy": np.__version__, "pandas": pd.__version__},
            },
            data_cfg["metadata_json"],
        )
