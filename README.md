# ChandiSVRPBench (`chandisvrp`)

A modular, runnable benchmark scaffold for **stochastic vehicle routing** on Chandigarh-like road networks.

## Features

- **OSMnx graph loader** for Chandigarh with **offline synthetic grid fallback**.
- **Instance generation** with heterogeneous customer demand and residential/commercial time windows.
- **Multiple solver baselines**:
  - OR-Tools CVRP/VRPTW (highly recommended baseline)
  - Random and Nearest-neighbor (simple baselines)
  - Nearest-neighbor + 2-opt (fast heuristic)
  - Metaheuristic baselines (ABC, ACO, ALNS, Hybrid) implemented as simplified permutation-based searches.
- **Stochastic travel-time simulation**:
  - Two Gaussian peak congestion windows (AM/PM peaks).
  - Distance-dependent congestion scaling.
  - Time-varying lognormal multiplicative delay.
  - Probabilistic accidents with configurable delays.
- **Monte Carlo evaluation** outputs CSV/JSON metrics with statistical aggregation and run-to-run variation.
- **Deterministic PDF report** generation using `reportlab`.
- **Interactive route visualization** using `folium`.
- **Typer CLI** for full pipeline execution and modular commands.

## Install

```bash
python -m pip install -r requirements.txt
```

## Quick Start

### One-file run (recommended)

```bash
python run_chandisvrp.py
```

This runs the full pipeline end-to-end and produces:
- `results/results.csv`: Detailed results for every run.
- `results/summary.csv`: Aggregated metrics per instance and solver, plus run-to-run variation fields.
- `reports/benchmark_report.pdf`: PDF summary with performance plots.
- `reports/interactive_map.html`: Folium map of the best route for the first instance (auto-opened).

### Advanced CLI Usage

```bash
# Run full pipeline with custom config
python -m chandisvrp.cli run-all --config configs/benchmark_small.yaml

# Individual steps
python -m chandisvrp.cli download-osm --place "Chandigarh, India"
python -m chandisvrp.cli build-instances --config configs/default.yaml
python -m chandisvrp.cli run-benchmark --config configs/benchmark_small.yaml
python -m chandisvrp.cli make-report --results results/results.csv --summary results/summary.csv --out reports/benchmark_report.pdf

# Smoke test (~2 minutes)
python scripts/smoke_test.py
```

## Configuration

The project uses YAML configuration files. You can use the `inherits` key to build upon base configurations.

Key configuration blocks:
- `seed`: Global random seed for reproducibility.
- `instance`: Parameters for instance generation (number of customers, vehicle capacity, etc.).
- `stochastic`: Parameters for the travel-time model, including `start_hour` and `peak_hours`.
- `evaluation`: Benchmark settings like `mc_rollouts` and `time_limit_s`.

## Stochastic Model & Execution Note

- **Start Time**: By default, vehicles depart the depot at 08:00 AM (`start_hour: 8.0` in config).
- **Coordinate Handling**: The benchmark automatically detects whether it's using real-world coordinates (lat/lon) or synthetic grid coordinates (meters) for visualization.
- **Interpretation Aids**: Reports include cost gap vs best, cost vs solve time scatter, cost per delivery trends, and feasibility vs size.
- **Solver Baselines**: Note that ABC, ACO, and ALNS solvers are implemented as **simplified baseline heuristics** to demonstrate the scaffold. For high-performance research, users are encouraged to plug in more advanced implementations into `src/chandisvrp/solvers/`.

## Project Layout

- `src/chandisvrp/`: Core library code.
  - `geo/`: Graph loading and processing.
  - `instances/`: Problem instance generation and I/O.
  - `solvers/`: VRP solver implementations.
  - `stochastic/`: Simulation and travel-time models.
  - `reporting/`: PDF and map generation.
- `configs/`: YAML configuration files.
- `scripts/`: Helper scripts for individual pipeline stages.
- `data/`: Instances and processed graphs.
- `results/`: CSV outputs and metadata.
- `reports/`: PDF reports and HTML maps.

## Requirements

- Python 3.8+
- `osmnx` & `networkx` for graph handling.
- `ortools` for the OR-Tools solver.
- `folium` for interactive maps.
- `reportlab` for PDF generation.
- `typer`, `pandas`, `numpy`, `yaml` for infrastructure.
