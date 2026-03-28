from types import GenericAlias

from foxhound.core.model.base_model import BaseModel


class ComponentMetadata(BaseModel):
    qualifier: str | None = None
    primary: bool = False
    kind: type | GenericAlias
