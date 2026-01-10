from typing import Callable, Generic, TypeVar

from foxhound.core.base_model import BaseModel
from foxhound.core.component_metadata import ComponentMetadata

T = TypeVar('T')


class ComponentDefinition(BaseModel, Generic[T]):
    component_metadata: ComponentMetadata[T]
    inflator: Callable[..., T]
    param_qualifiers: dict[str, str] = {}
