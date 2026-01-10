from typing import TypeVar, Generic, Callable, Dict

from foxhound.core.base_model import BaseModel
from foxhound.core.component_metadata import ComponentMetadata

T = TypeVar('T')


class ComponentDefinition(BaseModel, Generic[T]):
    component_metadata: ComponentMetadata[T]
    inflator: Callable[..., T]
    param_qualifiers: Dict[str, str] = {}
