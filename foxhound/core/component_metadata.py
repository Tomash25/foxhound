from typing import Generic, TypeVar

from foxhound.core.base_model import BaseModel

T = TypeVar('T')


class ComponentMetadata(BaseModel, Generic[T]):
    qualifier: str | None = None
    kind: type[T]
