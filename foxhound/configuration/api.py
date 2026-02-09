import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from foxhound import ComponentDefinition, define_component
from foxhound.configuration.configuration_reader import ConfigurationReader, ConfigurationSection
from foxhound.core.api import register_component_definition
from foxhound.core.base_model import BaseModel
from foxhound.core.typing_tools import simplify_parameters

T = TypeVar('T')

def configuration(
        section: str | None = None,
) -> type[T] | Callable[..., T]:
    def decorator(target: type[T] | Callable[..., T]) -> type[T] | Callable[..., T]:
        def inflator(reader: ConfigurationReader) -> T:
            try:
                return target(**_parse_parameters(target, reader.read(section)))
            except TypeError as e:
                raise TypeError(f'Cannot load {target} from configuration at section "{section}"') from e

        component_definition: ComponentDefinition[T] = define_component(target)
        component_definition.inflator = inflator
        register_component_definition(component_definition)

        return target

    return decorator


def _parse_parameters(
        target: type[T] | Callable[..., T],
        configuration_section: ConfigurationSection
) -> dict[str, Any]:
    parameter_types: dict[str, type[Any]] = simplify_parameters(inspect.signature(target))
    parsed_parameters: dict[str, Any] = {}

    for key, value in configuration_section.items():
        if key not in parameter_types:
            continue

        _type: type[Any] = parameter_types[key]

        try:
            if issubclass(_type, BaseModel):
                parsed_parameters[key] = _type.model_validate(value)
            else:
                parsed_parameters[key] = _type(value)
        except ValueError as e:
            raise TypeError(
                f'Cannot parse parameter "{key}" of {target} '
                f'from configuration value "{value}"'
            ) from e

    return parsed_parameters
