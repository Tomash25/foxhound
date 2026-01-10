from typing import Generic, TypeVar, Type, Optional

from foxhound.core.base_model import BaseModel

T = TypeVar('T')


class ComponentMetadata(BaseModel, Generic[T]):
    qualifier: Optional[str] = None
    kind: Type[T]
