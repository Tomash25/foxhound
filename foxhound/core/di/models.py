from collections.abc import Callable
from types import GenericAlias
from typing import Generic, TypeVar, get_origin

from pydantic import model_validator

from foxhound.core.models import BaseModel

T = TypeVar('T')

class Parameter(BaseModel):
    name: str
    kind: type | GenericAlias
    qualifier: str | None = None
    parent_component_id: str


class ComponentMetadata(BaseModel):
    id: str
    qualifier: str | None = None
    primary: bool = False
    kind: type | GenericAlias


class Component(BaseModel, Generic[T]):
    metadata: ComponentMetadata
    value: T

    @model_validator(mode='after')
    def _validate_type_match(self) -> 'Component[T]':
        kind: type | GenericAlias = self.metadata.kind
        expected_type: type | GenericAlias = kind if get_origin(kind) is None else get_origin(kind)
        actual_value: T = self.value

        if not isinstance(actual_value, expected_type):
            raise ValueError(
                f'Component value type mismatch: expected {expected_type}, '
                f'but got {type(actual_value)}'
            )

        return self


class ComponentDefinition(BaseModel, Generic[T]):
    metadata: ComponentMetadata
    inflator: Callable[..., T]
    param_qualifiers: dict[str, str] = {}

