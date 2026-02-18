# ChandiSVRPBench (`chandisvrp`)

A modular, runnable benchmark scaffold for **stochastic vehicle routing** on Chandigarh-like road networks.

## Features

- OSMnx graph loader for Chandigarh with **offline synthetic grid fallback**.
- Instance generation with heterogeneous customer demand and residential/commercial time windows.
- Multiple solver baselines:
  - OR-Tools CVRP/VRPTW
  - Nearest-neighbor + 2-opt
  - ABC (Artificial Bee Colony)
  - ACO (Ant Colony Optimization)
  - Hybrid ACO→ABC
  - ALNS (destroy/repair with adaptive weights)
- Stochastic travel-time simulation with:
  - two Gaussian peak congestion windows,
  - distance-dependent congestion scaling,
  - time-varying lognormal multiplicative delay,
  - probabilistic accidents.
- Monte Carlo evaluation outputs CSV/JSON metrics.
- Deterministic PDF report generation.
- Typer CLI for full pipeline execution.

## Install

```bash
python -m pip install -r requirements.txt
```

## One-file run (recommended)

```bash
python run_chandisvrp.py
```

This runs the full pipeline end-to-end and produces:
- `results/results.csv`
- `results/summary.csv`
- `reports/benchmark_report.pdf`
- `reports/interactive_map.html` (auto-opened in browser)

## Advanced CLI

```bash
python -m chandisvrp.cli run-all --config configs/benchmark_small.yaml --map-out reports/interactive_map.html --open-map True
python -m chandisvrp.cli download-osm --place "Chandigarh, India"
python -m chandisvrp.cli build-instances --config configs/default.yaml
python -m chandisvrp.cli run-benchmark --config configs/benchmark_small.yaml
python -m chandisvrp.cli make-report --results results/results.csv --summary results/summary.csv --out reports/benchmark_report.pdf
python scripts/smoke_test.py
```

> Smoke test is designed to complete quickly (≈2 minutes target), and will use synthetic graph fallback when offline.

## Outputs

- `results/results.csv` (per instance, solver, seed)
- `results/summary.csv` (aggregated per instance+solver)
- `results/run_metadata.json`
- `reports/benchmark_report.pdf`

## Project Layout

See `src/chandisvrp/` for modular components and `scripts/` for helper executables.
