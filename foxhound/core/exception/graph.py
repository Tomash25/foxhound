from typing import Any, Hashable

from networkx import DiGraph
from networkx.algorithms.cycles import simple_cycles


class CyclicGraphError(Exception):
    graph: DiGraph
    cycles: list[Hashable | Any]

    def __init__(self, graph: DiGraph):
        self.graph = graph
        self.cycles = list(simple_cycles(graph))
        formatted_cycles: list[str] = [' → '.join(c + c[:1]) for c in self.cycles]
        super().__init__(f'Cyclic dependencies detected: {"; ".join(formatted_cycles)}')
