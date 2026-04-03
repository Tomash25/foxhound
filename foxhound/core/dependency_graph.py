from enum import Enum

from networkx import DiGraph, is_directed_acyclic_graph

from foxhound.core.dependency_resolver import DependencyResolver
from foxhound.core.exception.dependency import UnsatisfiedDependenciesError
from foxhound.core.exception.graph import CyclicGraphError
from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.parameter import Parameter
from foxhound.core.model.result import Result
from foxhound.core.parameter_tools import parse_parameters


class NodeType(Enum):
    COMPONENT = 'COMPONENT'
    PARAMETER = 'PARAMETER'


class DependencyGraphMapper:
    _dependency_resolver: DependencyResolver

    def __init__(self, dependency_resolver: DependencyResolver) -> None:
        self._dependency_resolver = dependency_resolver

    def map(self, component_definitions: list[ComponentDefinition]) -> Result[DiGraph]:
        self._assert_unique_qualifiers(component_definitions)

        graph: DiGraph = DiGraph()
        self._map_components(graph, component_definitions)

        dependency_mapping: Result[None] = self._map_dependencies(graph, component_definitions)

        if not dependency_mapping.successful:
            return Result.incomplete(graph, dependency_mapping.exception)

        if not is_directed_acyclic_graph(graph):
            return Result.bad(graph, CyclicGraphError(graph))

        return Result.ok(graph)

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

                graph.add_edge(component_node_id, parameter_node_id)

    def _map_dependencies(self, graph: DiGraph, definitions: list[ComponentDefinition]) -> Result[None]:
        all_parameters: dict[str, Parameter] = self._filter_parameter_nodes(graph)
        mapping_failures: dict[Parameter, str] = {}

        for parameter_node_id, parameter in all_parameters.items():
            dependency_resolution: Result[str] = self._dependency_resolver.try_resolve(parameter, definitions)

            if dependency_resolution.successful:
                graph.add_edge(parameter_node_id, dependency_resolution.value)
            else:
                mapping_failures[parameter] = dependency_resolution.hint

        if len(mapping_failures) != 0:
            return Result.error(UnsatisfiedDependenciesError(mapping_failures))

        return Result.ok(None)

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
