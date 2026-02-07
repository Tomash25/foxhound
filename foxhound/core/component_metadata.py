from types import GenericAlias

from foxhound.core.base_model import BaseModel


class ComponentMetadata(BaseModel):
    qualifier: str | None = None
    kind: type | GenericAlias
