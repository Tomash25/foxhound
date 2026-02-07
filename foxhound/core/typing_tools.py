import inspect
from inspect import Signature
from typing import Any, Union, get_args, get_origin


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


def is_assignable_to(candidate: type, requested: type) -> bool:
    target_generic: bool = is_generic(candidate)
    request_generic: bool = is_generic(requested)

    if target_generic != request_generic:
        return False

    if not request_generic:
        return issubclass(candidate, requested)

    if not issubclass(get_origin(candidate), get_origin(requested)):
        return False

    return get_args(candidate) == get_args(requested)


def is_generic(target: type) -> bool:
    return get_origin(target) is not None


def simplify_parameters(signature: Signature) -> dict[str, type[Any]]:
    return {
        name: param.annotation
        for name, param in signature.parameters.items()
        if param.annotation is not param.empty
    }
