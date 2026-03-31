from types import GenericAlias

from foxhound.core.model.base_model import BaseModel


class Parameter(BaseModel):
    name: str
    kind: type | GenericAlias
    qualifier: str | None = None
