from collections.abc import Callable
from typing import Any, TypeVar

from foxhound.core.component import Component
from foxhound.core.component_definition import ComponentDefinition
from foxhound.core.container import Container
from foxhound.core.result import Result
from foxhound.core.wiring import try_wire_dependencies

T = TypeVar('T')


def inflate(container: Container, component_definitions: list[ComponentDefinition[Any]]) -> None:
    inflation_tasks: list[ComponentDefinition] = component_definitions.copy()

    while len(inflation_tasks) > 0:
        progressed: bool = False

        for task in inflation_tasks.copy():
            wiring_result: Result[Callable[[], Any]] = try_wire_dependencies(
                task.inflator,
                task.param_qualifiers,
                container
            )

            if not wiring_result.successful:
                continue

            progressed = True
            value: Any = wiring_result.value()

            if value is not None:
                container.register_component(Component(metadata=task.component_metadata, value=value))

            inflation_tasks.remove(task)

        if not progressed:
            raise _analyze_wiring_issue(inflation_tasks, container)


def _analyze_wiring_issue(
        component_definitions: list[ComponentDefinition[Any]],
        container: Container
) -> Exception:
    for definition in component_definitions:
        wiring_result: Result[Callable[[], Any]] = try_wire_dependencies(
            definition.inflator,
            definition.param_qualifiers,
            container
        )

        if not wiring_result.successful:
            return wiring_result.exception

    return RuntimeError('Could not analyze wiring issue')
