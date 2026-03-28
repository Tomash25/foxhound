from collections.abc import Callable
from typing import Generic, TypeVar

from foxhound.core.model.base_model import BaseModel
from foxhound.core.model.component_metadata import ComponentMetadata

T = TypeVar('T')


class ComponentDefinition(BaseModel, Generic[T]):
    id: str
    component_metadata: ComponentMetadata
    inflator: Callable[..., T]
    param_qualifiers: dict[str, str] = {}
