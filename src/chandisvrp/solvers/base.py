from __future__ import annotations

from abc import ABC, abstractmethod

import networkx as nx
import numpy as np

from chandisvrp.types import Instance, RoutePlan


class Solver(ABC):
    name: str

    @abstractmethod
    def solve(self, g: nx.MultiDiGraph, instance: Instance, rng: np.random.Generator, time_limit_s: float) -> RoutePlan:
        raise NotImplementedError
