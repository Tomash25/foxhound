import inspect
from collections.abc import Callable
from types import GenericAlias, ModuleType
from typing import TypeVar

from networkx.classes import DiGraph

from foxhound.core.di.component_scanner import ComponentScanner
from foxhound.core.di.consts import OBJECT_COMPONENT_DEFINITION_ATTRIBUTE
from foxhound.core.di.container import Container
from foxhound.core.di.dependency_resolver import DependencyResolver
from foxhound.core.di.graph.inflator import DependencyGraphInflator
from foxhound.core.di.graph.mapper import DependencyGraphMapper
from foxhound.core.di.models import ComponentDefinition, ComponentMetadata
from foxhound.core.models import Result
from foxhound.core.utils.typing import validate_concrete_parameters, validate_concrete_return_type

T = TypeVar('T')


def component(
        qualifier: str | None = None,
        primary: bool = False,
        param_qualifiers: dict[str, str] | None = None
) -> type[T] | Callable[..., T]:
    def decorator(target: type[T] | Callable[..., T]) -> type[T] | Callable[..., T]:
        component_definition: ComponentDefinition[T] = define_component(target, qualifier, primary, param_qualifiers)
        embed_definition(target, component_definition)
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


def embed_definition(target: type[T] | Callable[..., T], component_definition: ComponentDefinition[T]):
    setattr(target, OBJECT_COMPONENT_DEFINITION_ATTRIBUTE, component_definition)


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


def start(*scan_modules: str | ModuleType) -> None:
    component_scanner: ComponentScanner = ComponentScanner()
    dependency_resolver: DependencyResolver = DependencyResolver()
    graph_mapper: DependencyGraphMapper = DependencyGraphMapper(dependency_resolver)

    dependency_graph_mapping: Result[DiGraph] = graph_mapper.map(
        component_scanner.scan(set(scan_modules))
    )

    if not dependency_graph_mapping.successful:
        raise dependency_graph_mapping.exception

    DependencyGraphInflator().inflate(
        dependency_graph_mapping.value,
        Container()
    )
