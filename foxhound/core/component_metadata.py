from typing import Generic, Optional, TypeVar

from foxhound.core.base_model import BaseModel

T = TypeVar('T')


class ComponentMetadata(BaseModel, Generic[T]):
    qualifier: Optional[str] = None
    kind: type[T]
