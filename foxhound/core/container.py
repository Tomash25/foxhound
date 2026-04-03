from typing import Any, TypeVar

from foxhound.core.model.component import Component
from foxhound.core.typing_tools import is_assignable_to

T = TypeVar('T')


class Container:
    inflated: bool
    _components: dict[str, Component[Any]]

    def __init__(self):
        self.inflated = False
        self._components = {}

    def register_component(self, component: Component[Any]) -> None:
        qualifier: str | None = component.metadata.qualifier

        if qualifier is not None and self._already_exists(qualifier):
            raise ValueError(
                f'A component with qualifier "{qualifier}" already exists'
            )

        self._components[component.metadata.id] = component

    def get_component(self, component_id: str) -> Component[Any]:
        return self._components[component_id]

    def _already_exists(self, qualifier: str) -> bool:
        return any(component.metadata.qualifier == qualifier for component in self._components.values())

    def get_components(self, kind: type[T]) -> list[Component[T]]:
        return list(
            filter(
                lambda component: is_assignable_to(component.metadata.kind, kind),
                self._components.values()
            )
        )
