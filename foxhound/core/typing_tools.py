import inspect
from inspect import Signature
from typing import Any, Union, get_origin


def validate_concrete_parameters(signature: inspect.Signature) -> None:
    for name, parameter in signature.parameters.items():
        if parameter.annotation == inspect.Parameter.empty:
            raise TypeError(f'Parameter "{name}" is missing type hinting annotation')
        if is_union_type(parameter.annotation):
            raise TypeError(f'Parameter "{name}" is type hinted as a union type')


def validate_concrete_return_type(signature: inspect.Signature) -> None:
    if signature.return_annotation == inspect.Signature.empty:
        raise TypeError('Signature is missing a return type hinting annotation')
    if is_union_type(signature.return_annotation):
        raise TypeError('Return type is hinted as a union type')


def is_union_type(annotation: Any) -> bool:
    origin: type = get_origin(annotation)
    return origin is Union or (hasattr(origin, '__name__') and origin.__name__ == 'UnionType')


def simplify_parameters(signature: Signature) -> dict[str, type[Any]]:
    return {
        name: param.annotation
        for name, param in signature.parameters.items()
        if param.annotation is not param.empty
    }
