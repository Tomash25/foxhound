import inspect
from typing import Any

from networkx import DiGraph

from foxhound.core.component_definition import ComponentDefinition
from foxhound.core.component_metadata import ComponentMetadata
from foxhound.core.typing_tools import is_assignable_to, simplify_parameters


def map_dependency_graph(component_definitions: list[ComponentDefinition]) -> DiGraph:
    _assert_unique_qualifiers(component_definitions)

    graph: DiGraph = DiGraph()
    _create_nodes(graph, component_definitions)
    _map_edges(graph)

    return graph


def _create_nodes(graph: DiGraph, component_definitions: list[ComponentDefinition]) -> None:
    for component_definition in component_definitions:
        graph.add_node(
            component_definition.id,
            definition=component_definition
        )


def _map_edges(graph: DiGraph):
    for node_id, properties in graph.nodes(data=True):
        definition: ComponentDefinition = properties.get('definition')
        dependencies: dict[str, type[Any]] = _infer_dependencies(definition)

        for name, kind in dependencies.items():
            qualifier: str | None = definition.param_qualifiers.get(name)
            dependency_node_id: str | None = _try_find_dependency(graph, kind, qualifier)

            if dependency_node_id is not None:
                graph.add_edge(node_id, dependency_node_id)


def _try_find_dependency(graph: DiGraph, kind: type, qualifier: str | None) -> str | None:
    if qualifier is None:
        return _find_unqualified_component(graph, kind)

    return _find_qualified_component(graph, kind, qualifier)


def _find_qualified_component(graph: DiGraph, kind: type, qualifier: str) -> str | None:
    for node_id, properties in graph.nodes(data=True):
        metadata: ComponentMetadata = properties.get('definition').component_metadata

        if is_assignable_to(metadata.kind, kind) and metadata.qualifier == qualifier:
            return node_id

    return None


def _find_unqualified_component(graph: DiGraph, kind: type) -> str | None:
    matches: list[tuple[str, ComponentDefinition]] = [
        (node_id, properties.get('definition'))
        for node_id, properties in graph.nodes(data=True)
        if is_assignable_to(properties.get('definition').component_metadata.kind, kind)
    ]

    if len(matches) == 1:
        return matches[0][0]

    primary_matches: list[str] = [
        node_id for node_id, definition in matches
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


def _infer_dependencies(component_definition: ComponentDefinition) -> dict[str, type[Any]]:
    return simplify_parameters(inspect.signature(component_definition.inflator))
