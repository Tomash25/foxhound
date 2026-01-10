import inspect
from typing import TypeVar, Callable, Any, Dict, Type, List, Optional

from foxhound.core.component import Component
from foxhound.core.container import Container
from foxhound.core.result import Result
from foxhound.core.signature_tools import simplify_parameters

T = TypeVar('T')


def try_wire_dependencies(
        func: Callable[..., T],
        param_qualifiers: Dict[str, str],
        container: Container
) -> Result[Callable[[], T]]:
    dependencies: Dict[str, Type[Any]] = _infer_dependencies(func)
    implementations: List[Any] = []

    for name, kind in dependencies.items():
        qualifier: Optional[str] = param_qualifiers.get(name)
        component_lookup: Result[Any] = _find_component(container, kind, qualifier)

        if not component_lookup.successful:
            return Result.fail(component_lookup.exception)

        implementations.append(component_lookup.value.value)

    return Result.ok(lambda: func(*implementations))


def _find_component(container: Container, kind: Type[T], qualifier: Optional[str]) -> Result[Component[T]]:
    if qualifier is None:
        return _find_unqualified_component(container, kind)

    return _find_qualified_component(container, kind, qualifier)


def _find_qualified_component(container: Container, kind: Type[T], qualifier: str) -> Result[Component[T]]:
    potential_matches: List[Component[T]] = container.get_components(kind)

    for component in potential_matches:
        if component.metadata.qualifier == qualifier:
            return Result.ok(component)

    if len(potential_matches) > 0:
        return Result.fail(
            ValueError(
                f'No registered component of {kind} with qualifier "{qualifier}". '
                f'However, {len(potential_matches)} other components of the same kind are registered.'
            )
        )

    return Result.fail(
        ValueError(
            f'No registered component of {kind} with qualifier "{qualifier}". '
            f'In fact, no component of {kind} has been found at all.'
        )
    )


def _find_unqualified_component(container: Container, kind: Type[T]) -> Result[Component[T]]:
    matching_components: List[Component[T]] = container.get_components(kind)

    if len(matching_components) < 1:
        return Result.fail(ValueError(f'No registered component of {kind}'))
    if len(matching_components) == 1:
        return Result.ok(matching_components[0])

    return Result.fail(
        ValueError(
            f'Multiple components of {kind} were found. '
            f'Specific component can be selected by specifying a qualifier.'
        )
    )


def _infer_dependencies(func: Callable[..., Any]) -> Dict[str, Type[Any]]:
    return simplify_parameters(inspect.signature(func))
