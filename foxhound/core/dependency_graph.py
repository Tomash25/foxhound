from enum import Enum

from networkx import DiGraph

from foxhound.core.model.result import Result
from foxhound.core.dependency_resolver import DependencyResolver
from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.parameter import Parameter
from foxhound.core.parameter_tools import parse_parameters


class NodeType(Enum):
    COMPONENT = 'COMPONENT'
    PARAMETER = 'PARAMETER'


class DependencyGraphMapper:
    def __init__(self, dependency_resolver: DependencyResolver) -> None:
        self._dependency_resolver = dependency_resolver

    def map(self, component_definitions: list[ComponentDefinition]) -> DiGraph:
        self._assert_unique_qualifiers(component_definitions)

        graph: DiGraph = DiGraph()
        self._map_components(graph, component_definitions)
        self._map_dependencies(graph, component_definitions)

        return graph

    def _map_components(self, graph: DiGraph, component_definitions: list[ComponentDefinition]) -> None:
        for definition in component_definitions:
            component_node_id: str = definition.id

            graph.add_node(
                component_node_id,
                type=NodeType.COMPONENT,
                definition=definition
            )

            parameters: list[Parameter] = parse_parameters(definition)

            for parameter in parameters:
                parameter_node_id: str = f'{parameter.name}@{component_node_id}'

                graph.add_node(
                    parameter_node_id,
                    type=NodeType.PARAMETER,
                    properties=parameter
                )

                graph.add_edge(parameter_node_id, component_node_id)

    def _map_dependencies(self, graph: DiGraph, definitions: list[ComponentDefinition]) -> dict[Parameter, Result[str]]:
        mapping_results: dict[Parameter, Result[str]] = {}
        all_parameters: dict[str, Parameter] = self._filter_parameter_nodes(graph)

        for parameter_node_id, parameter in all_parameters.items():
            dependency_resolution: Result[str] = self._dependency_resolver.try_resolve(parameter, definitions)

            if dependency_resolution.successful:
                graph.add_edge(parameter_node_id, dependency_resolution.value)

            mapping_results[parameter] = dependency_resolution

        return mapping_results

    def _assert_unique_qualifiers(self, component_definitions: list[ComponentDefinition]) -> None:
        for definition in component_definitions:
            qualifier: str | None = definition.component_metadata.qualifier

            if qualifier is None:
                continue

            qualifier_count: int = len([
                d for d in component_definitions
                if d.component_metadata.qualifier == qualifier
            ])

            if qualifier_count > 1:
                raise ValueError(
                    f'{qualifier_count} components are qualified with "{qualifier}". '
                    f'Qualifiers must be unique.'
                )

    def _filter_parameter_nodes(self, graph: DiGraph) -> dict[str, Parameter]:
        return {
            node_id: additional_data['properties'] for node_id, additional_data in graph.nodes(data=True)
            if additional_data['type'] == NodeType.PARAMETER
        }
