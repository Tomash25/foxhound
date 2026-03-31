from abc import ABC, abstractmethod

from foxhound import ComponentDefinition
from foxhound.core.model.parameter import Parameter


class DependencyResolver(ABC):
    @abstractmethod
    def try_resolve(
            self,
            dependency: Parameter,
            candidates: list[ComponentDefinition]
    ) -> tuple[str | None, str | None]:
        ...
