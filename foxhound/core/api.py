import inspect
import logging
from collections.abc import Callable
from types import GenericAlias
from typing import Any, TypeVar

from foxhound.core.component_definition import ComponentDefinition
from foxhound.core.component_metadata import ComponentMetadata
from foxhound.core.container import Container
from foxhound.core.inflation import inflate
from foxhound.core.result import Result
from foxhound.core.typing_tools import validate_concrete_parameters, validate_concrete_return_type
from foxhound.core.wiring import try_wire_dependencies
from foxhound.core.wiring_task import WiringTask

_CONTAINER = Container()
_INFLATED = False
_COMPONENT_DEFINITIONS: list[ComponentDefinition[Any]] = []
_WIRING_TASKS: list[WiringTask] = []

T = TypeVar('T')


def component(
        qualifier: str | None = None,
        param_qualifiers: dict[str, str] | None = None
) -> type[T] | Callable[..., T]:
    def decorator(target: type[T] | Callable[..., T]) -> type[T] | Callable[..., T]:
        component_definition: ComponentDefinition[T] = define_component(target, qualifier, param_qualifiers)
        register_component_definition(component_definition)
        return target

    return decorator


def define_component(
        target: type[T] | Callable[..., T],
        qualifier: str | None = None,
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
        component_metadata=ComponentMetadata(
            qualifier=qualifier,
            kind=return_type
        ),
        param_qualifiers={} if param_qualifiers is None else param_qualifiers,
        inflator=target
    )


def register_component_definition(definition: ComponentDefinition[T]) -> None:
    _COMPONENT_DEFINITIONS.append(definition)


def wire(
        param_qualifiers: dict[str, str] | None = None
) -> Callable[[Callable[..., T]], Callable[[], T]]:
    def decorator(func: Callable[..., T]) -> Callable[[], T]:
        signature: inspect.Signature = inspect.signature(func)
        _validate_function_signature(signature)

        def wrapper() -> T:
            if not _INFLATED:
                logging.warning('Cannot wire dependencies; container isn\'t inflated. Make sure start() was called')
                pass

            wiring_result: Result[Callable[[], T]] = try_wire_dependencies(
                func, {} if param_qualifiers is None else param_qualifiers, _CONTAINER
            )

            if wiring_result.successful:
                wired_func: Callable[[], T] = wiring_result.value
                return wired_func()

            raise wiring_result.exception

        return wrapper

    return decorator


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
