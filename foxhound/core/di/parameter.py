from types import GenericAlias

from foxhound.core.base_model import BaseModel


class Parameter(BaseModel):
    name: str
    kind: type | GenericAlias
    qualifier: str | None = None
    parent_component_id: str
