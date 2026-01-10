import inspect
from inspect import Signature
from typing import Any


def parameters_hinted(signature: Signature) -> bool:
    return all(parameter.annotation != inspect.Parameter.empty for parameter in signature.parameters.values())


def fully_hinted(signature: Signature):
    return parameters_hinted(signature) and signature.return_annotation != inspect.Signature.empty


def simplify_parameters(signature: Signature) -> dict[str, type[Any]]:
    return {
        name: param.annotation
        for name, param in signature.parameters.items()
        if param.annotation is not param.empty
    }
