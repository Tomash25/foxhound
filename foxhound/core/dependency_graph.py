import inspect
from enum import Enum
from typing import Any

from networkx import DiGraph

from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.component_metadata import ComponentMetadata
from foxhound.core.typing_tools import is_assignable_to, simplify_parameters


class NodeType(Enum):
    COMPONENT = 'COMPONENT'
    PARAMETER = 'PARAMETER'


def map_dependency_graph(component_definitions: list[ComponentDefinition]) -> DiGraph:
    _assert_unique_qualifiers(component_definitions)

    graph: DiGraph = DiGraph()
    _map_components(graph, component_definitions)
    _map_dependencies(graph)

    return graph


def _map_components(graph: DiGraph, component_definitions: list[ComponentDefinition]) -> None:
    for definition in component_definitions:
        component_node_id: str = definition.id

        graph.add_node(
            component_node_id,
            type=NodeType.COMPONENT,
            definition=definition
        )

        parameters: dict[str, type[Any]] = _simplify_parameters(definition)

        for name, kind in parameters.items():
            parameter_node_id: str = f'{name}@{component_node_id}'

            graph.add_node(
                parameter_node_id,
                type=NodeType.PARAMETER,
                name=name,
                kind=kind,
                qualifier=definition.param_qualifiers.get(name)
            )

            graph.add_edge(parameter_node_id, component_node_id)


def _map_dependencies(graph: DiGraph):
    all_parameters: list[tuple[str, dict[str, Any]]] = _filter_node_type(graph, NodeType.PARAMETER)

    for parameter_id, properties in all_parameters:
        kind: type = properties.get('kind')
        qualifier: str | None = properties.get('qualifier')

        satisfying_component_id: str | None = _try_find_dependency(graph, kind, qualifier)

        if satisfying_component_id is not None:
            graph.add_edge(parameter_id, satisfying_component_id)


def _try_find_dependency(graph: DiGraph, kind: type, qualifier: str | None) -> str | None:
    if qualifier is None:
        return _find_unqualified_component(graph, kind)

    return _find_qualified_component(graph, kind, qualifier)


def _find_qualified_component(graph: DiGraph, kind: type, qualifier: str) -> str | None:
    all_components: list[tuple[str, dict[str, Any]]] = _filter_node_type(graph, NodeType.COMPONENT)

    for component_id, properties in all_components:
        metadata: ComponentMetadata = properties.get('definition').component_metadata

        if is_assignable_to(metadata.kind, kind) and metadata.qualifier == qualifier:
            return component_id

    return None


def _find_unqualified_component(graph: DiGraph, kind: type) -> str | None:
    all_components: list[tuple[str, dict[str, Any]]] = _filter_node_type(graph, NodeType.COMPONENT)

    matches: list[tuple[str, ComponentDefinition]] = [
        (component_id, properties.get('definition'))
        for component_id, properties in all_components
        if is_assignable_to(properties.get('definition').component_metadata.kind, kind)
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


def _assert_unique_qualifiers(component_definitions: list[ComponentDefinition]) -> None:
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


def _filter_node_type(graph: DiGraph, node_type: NodeType) -> list[tuple[str, dict[str, Any]]]:
    return [
        (node_id, properties) for node_id, properties in graph.nodes(data=True)
        if properties.get('type') == node_type
    ]


def _simplify_parameters(component_definition: ComponentDefinition) -> dict[str, type[Any]]:
    return simplify_parameters(inspect.signature(component_definition.inflator))
