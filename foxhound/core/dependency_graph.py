import inspect
from enum import Enum
from typing import Any

from networkx import DiGraph

from foxhound import ComponentMetadata
from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.parameter import Parameter
from foxhound.core.parameter_tools import parse_parameters
from foxhound.core.typing_tools import simplify_arguments, is_assignable_to


class NodeType(Enum):
    COMPONENT = 'COMPONENT'
    PARAMETER = 'PARAMETER'


class DependencyGraphMapper:
    def map_dependency_graph(self, component_definitions: list[ComponentDefinition]) -> DiGraph:
        self._assert_unique_qualifiers(component_definitions)

        graph: DiGraph = DiGraph()
        self._map_components(graph, component_definitions)
        self._map_dependencies(graph)

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

    def _map_dependencies(self, graph: DiGraph):
        all_parameters: list[tuple[str, dict[str, Any]]] = self._filter_node_type(graph, NodeType.PARAMETER)

        for parameter_id, additional_data in all_parameters:
            properties: Parameter = additional_data['properties']

            satisfying_component_id: str | None = self._try_find_dependency(
                graph,
                properties.kind,
                properties.qualifier
            )

            if satisfying_component_id is not None:
                graph.add_edge(parameter_id, satisfying_component_id)

    def _try_find_dependency(self, graph: DiGraph, kind: type, qualifier: str | None) -> str | None:
        if qualifier is None:
            return self._find_unqualified_component(graph, kind)

        return self._find_qualified_component(graph, kind, qualifier)

    def _find_qualified_component(self, graph: DiGraph, kind: type, qualifier: str) -> str | None:
        all_components: list[tuple[str, dict[str, Any]]] = self._filter_node_type(graph, NodeType.COMPONENT)

        for component_id, additional_data in all_components:
            metadata: ComponentMetadata = additional_data['definition'].component_metadata

            if is_assignable_to(metadata.kind, kind) and metadata.qualifier == qualifier:
                return component_id

        return None

    def _find_unqualified_component(self, graph: DiGraph, kind: type) -> str | None:
        all_components: list[tuple[str, dict[str, Any]]] = self._filter_node_type(graph, NodeType.COMPONENT)

        matches: list[tuple[str, ComponentDefinition]] = [
            (component_id, additional_data['definition'])
            for component_id, additional_data in all_components
            if is_assignable_to(additional_data['definition'].component_metadata.kind, kind)
        ]

        if len(matches) == 1:
            return matches[0][0]

        primary_matches: list[str] = [
            component_id for component_id, definition in matches
            if definition.component_metadata.primary
        ]

        if len(primary_matches) == 1:
            return primary_matches[0]

        return None

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

    def _filter_node_type(self, graph: DiGraph, node_type: NodeType) -> list[tuple[str, dict[str, Any]]]:
        return [
            (node_id, additional_data) for node_id, additional_data in graph.nodes(data=True)
            if additional_data['type'] == node_type
        ]

    def _simplify_parameters(self, component_definition: ComponentDefinition) -> dict[str, type[Any]]:
        return simplify_arguments(inspect.signature(component_definition.inflator))
