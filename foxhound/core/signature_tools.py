import inspect
from inspect import Signature

from typing import Dict, Any, Type


def parameters_hinted(signature: Signature) -> bool:
    for name, parameter in signature.parameters.items():
        if parameter.annotation == inspect.Parameter.empty:
            return False

    return True


def fully_hinted(signature: Signature):
    return parameters_hinted(signature) and signature.return_annotation != inspect.Signature.empty


def simplify_parameters(signature: Signature) -> Dict[str, Type[Any]]:
    return {
        name: param.annotation
        for name, param in signature.parameters.items()
        if param.annotation is not param.empty
    }
