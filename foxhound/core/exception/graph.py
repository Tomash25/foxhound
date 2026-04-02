from typing import Any, Hashable

from networkx import DiGraph
from networkx.algorithms.cycles import simple_cycles


class CyclicGraphError(Exception):
    graph: DiGraph
    cycles: list[Hashable | Any]

    def __init__(self, graph: DiGraph):
        formatted_cycles: list[str] = [' → '.join(c) for c in simple_cycles(graph)]
        self.graph = graph
        self.cycles = list(simple_cycles(graph))
        super().__init__(f'Cyclic dependencies detected: {"; ".join(formatted_cycles)}')
