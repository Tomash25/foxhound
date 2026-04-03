import inspect
import logging
from collections.abc import Callable
from types import GenericAlias
from typing import Any, TypeVar

from foxhound.core.container import Container
from foxhound.core.inflation import inflate
from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.component_metadata import ComponentMetadata
from foxhound.core.model.result import Result
from foxhound.core.model.wiring_task import WiringTask
from foxhound.core.typing_tools import validate_concrete_parameters, validate_concrete_return_type

_CONTAINER = Container()
_INFLATED = False
_COMPONENT_DEFINITIONS: list[ComponentDefinition[Any]] = []
_WIRING_TASKS: list[WiringTask] = []

T = TypeVar('T')

def component(
        qualifier: str | None = None,
        primary: bool = False,
        param_qualifiers: dict[str, str] | None = None
) -> type[T] | Callable[..., T]:
    def decorator(target: type[T] | Callable[..., T]) -> type[T] | Callable[..., T]:
        component_definition: ComponentDefinition[T] = define_component(target, qualifier, primary, param_qualifiers)
        register_component_definition(component_definition)
        return target

    return decorator


def define_component(
        target: type[T] | Callable[..., T],
        qualifier: str | None = None,
        primary: bool = False,
        param_qualifiers: dict[str, str] | None = None
) -> ComponentDefinition[T]:
    signature: inspect.Signature = inspect.signature(target)

    if inspect.isclass(target):
        _validate_ctor_signature(signature)
        return_type: type = target
    else:
        _validate_function_signature(signature)
        return_type: type | GenericAlias = signature.return_annotation

    return ComponentDefinition(
        metadata=ComponentMetadata(
            id=str(target),
            qualifier=qualifier,
            primary=primary,
            kind=return_type
        ),
        param_qualifiers={} if param_qualifiers is None else param_qualifiers,
        inflator=target
    )


def register_component_definition(definition: ComponentDefinition[T]) -> None:
    _COMPONENT_DEFINITIONS.append(definition)


def _validate_function_signature(signature: inspect.Signature) -> None:
    try:
        validate_concrete_parameters(signature)
    except TypeError as e:
        raise TypeError('Function parameters must be strongly type hinted for DI') from e

    try:
        validate_concrete_return_type(signature)
    except TypeError as e:
        raise TypeError('Function return type must be strongly hinted for DI') from e


def _validate_ctor_signature(signature: inspect.Signature) -> None:
    try:
        validate_concrete_parameters(signature)
    except TypeError as e:
        raise TypeError('Class constructor parameters must be strongly type hinted for DI') from e


def start() -> None:
    global _CONTAINER, _INFLATED

    if _INFLATED:
        return

    _CONTAINER = Container()
    inflate(_CONTAINER, _COMPONENT_DEFINITIONS)
    _INFLATED = True
