from networkx import DiGraph
from networkx.algorithms.cycles import simple_cycles


class CyclicGraphError(Exception):
    def __init__(self, graph: DiGraph):
        self.cycles = graph
        formatted_cycles: list[str] = [' → '.join(c) for c in simple_cycles(graph)]
        super().__init__(f'Cyclic dependencies detected: {"; ".join(formatted_cycles)}')
