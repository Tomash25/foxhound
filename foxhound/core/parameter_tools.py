import inspect
from typing import Any

from foxhound.core.di.component_definition import ComponentDefinition
from foxhound.core.di.parameter import Parameter
from foxhound.core.utils.typing import simplify_arguments


def parse_parameters(component_definition: ComponentDefinition) -> list[Parameter]:
    parameters: list[Parameter] = []

    arguments: dict[str, type[Any]] = simplify_arguments(
        inspect.signature(component_definition.inflator)
    )

    for name, kind in arguments.items():
        parameters.append(
            Parameter(
                name=name,
                kind=kind,
                qualifier=component_definition.param_qualifiers.get(name),
                parent_component_id=component_definition.metadata.id
            )
        )

    return parameters
