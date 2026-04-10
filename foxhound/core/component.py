from types import GenericAlias
from typing import Generic, TypeVar, get_origin

from pydantic import BaseModel, model_validator

from foxhound.core.component_metadata import ComponentMetadata

T = TypeVar('T')


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
