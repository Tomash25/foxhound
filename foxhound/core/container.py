from typing import Any, TypeVar

from foxhound.core.component import Component
from foxhound.core.typing_tools import is_assignable_to

T = TypeVar('T')


class Container:
    def __init__(self):
        self.inflated: bool = False
        self._components: list[Component[Any]] = []

    def register_component(self, component: Component[Any]) -> None:
        qualifier: str | None = component.metadata.qualifier

        if qualifier is not None and self._already_exists(qualifier):
            raise ValueError(
                f'A component with qualifier "{qualifier}" already exists'
            )

        self._components.append(component)

    def _already_exists(self, qualifier: str) -> bool:
        return any(component.metadata.qualifier == qualifier for component in self._components)

    def get_components(self, kind: type[T]) -> list[Component[T]]:
        return list(
            filter(
                lambda component: is_assignable_to(component.metadata.kind, kind),
                self._components
            )
        )
