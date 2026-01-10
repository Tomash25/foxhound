import inspect
import logging
from typing import Any, Callable, Optional, TypeVar

from foxhound.core.component_definition import ComponentDefinition
from foxhound.core.component_metadata import ComponentMetadata
from foxhound.core.container import Container
from foxhound.core.inflation import inflate
from foxhound.core.result import Result
from foxhound.core.signature_tools import fully_hinted, parameters_hinted
from foxhound.core.wiring import try_wire_dependencies
from foxhound.core.wiring_task import WiringTask

_CONTAINER = Container()
_INFLATED = False
_COMPONENT_DEFINITIONS: list[ComponentDefinition[Any]] = []
_WIRING_TASKS: list[WiringTask] = []

T = TypeVar('T')


def component(
        qualifier: Optional[str] = None,
        param_qualifiers: Optional[dict[str, str]] = None
) -> type[T] | Callable[..., T]:
    def decorator(target: type[T] | Callable[..., T]) -> type[T] | Callable[..., T]:
        component_definition: ComponentDefinition[T] = define_component(target, qualifier, param_qualifiers)
        _COMPONENT_DEFINITIONS.append(component_definition)
        return target

    return decorator


def define_component(
        target: type[T] | Callable[..., T],
        qualifier: Optional[str] = None,
        param_qualifiers: Optional[dict[str, str]] = None
) -> ComponentDefinition[T]:
    signature: inspect.Signature = inspect.signature(target)

    if inspect.isclass(target):
        assert parameters_hinted(signature), 'Component constructor parameters must be annotated with type hinting'
        return_type = target
    else:
        assert fully_hinted(signature), 'Component function must be fully annotated with type hinting'
        return_type: type[T] = signature.return_annotation

    return ComponentDefinition[return_type](
        component_metadata=ComponentMetadata[return_type](
            qualifier=qualifier,
            kind=return_type
        ),
        param_qualifiers={} if param_qualifiers is None else param_qualifiers,
        inflator=target
    )


def wire(
        param_qualifiers: Optional[dict[str, str]] = None
) -> Callable[[], T]:
    def decorator(func: Callable[..., T]) -> Callable[[], Callable[[], T]]:
        signature: inspect.Signature = inspect.signature(func)
        assert parameters_hinted(signature), 'Wired function parameters must be annotated with type hinting'

        def wrapper() -> Callable[[], T]:
            if not _INFLATED:
                logging.warning('Cannot wire dependencies; container isn\'t inflated. Make sure start() was called')
                pass

            wiring_result: Result[Callable[[], T]] = try_wire_dependencies(
                func, {} if param_qualifiers is None else param_qualifiers, _CONTAINER
            )

            if wiring_result.successful:
                return wiring_result.value()

            raise wiring_result.exception

        return wrapper

    return decorator


def start() -> None:
    global _CONTAINER, _INFLATED

    if _INFLATED:
        return

    _CONTAINER = Container()
    inflate(_CONTAINER, _COMPONENT_DEFINITIONS)
    _INFLATED = True
