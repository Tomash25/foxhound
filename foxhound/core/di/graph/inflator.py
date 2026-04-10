from typing import Any, Hashable

from networkx.classes import DiGraph

from foxhound.core.di.container import Container
from foxhound.core.di.graph.node_type import NodeType
from foxhound.core.di.component import Component
from foxhound.core.di.component_definition import ComponentDefinition


class DependencyGraphInflator:
    def inflate(self, graph: DiGraph, container: Container) -> None:
        root_components: list[Hashable] = [
            node for node in graph.nodes() if graph.in_degree(node) == 0
        ]

        for component_node in root_components:
            self._inflate_component(component_node, graph, container)

    def _inflate_component(self, component_node: Hashable, graph: DiGraph, container: Container) -> Any:
        assert graph.nodes[component_node].get('type') == NodeType.COMPONENT

        definition: ComponentDefinition = graph.nodes[component_node].get('definition')

        existing_component: Component[Any] | None = container.get_component(definition.metadata.id)

        if existing_component is not None:
            return existing_component.value

        inflated_parameters: dict[str, Any] = {}

        for parameter, dependency_nodes in self._parameter_dependency_nodes(component_node, graph).items():
            if len(dependency_nodes) == 1:
                inflated_parameters[parameter] = self._inflate_component(dependency_nodes[0], graph, container)
            else:
                inflated_parameters[parameter] = [
                    self._inflate_component(node, graph, container) for node in dependency_nodes
                ]

        inflated_value: Any = definition.inflator(**inflated_parameters)

        container.register_component(
            Component(
                metadata=definition.metadata,
                value=inflated_value,
            )
        )

        return inflated_value

    def _parameter_dependency_nodes(self, component_node: Hashable, graph: DiGraph) -> dict[str, list[Hashable]]:
        assert graph.nodes[component_node].get('type') == NodeType.COMPONENT

        parameter_nodes: list[Hashable] = list(graph.successors(component_node))

        assert all([
            graph.nodes[parameter_node].get('type') == NodeType.PARAMETER
            for parameter_node in parameter_nodes
        ])

        return {
            graph.nodes[parameter_node].get('properties').name: list(graph.successors(parameter_node))
            for parameter_node in parameter_nodes
        }
