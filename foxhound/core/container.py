from typing import List, TypeVar, Any, Type, Optional

from foxhound.core.component import Component

T = TypeVar('T')


class Container:
    def __init__(self):
        self.inflated: bool = False
        self._components: List[Component[Any]] = []

    def register_component(self, component: Component[Any]) -> None:
        qualifier: Optional[str] = component.metadata.qualifier

        if qualifier is not None and self._already_exists(qualifier):
            raise ValueError(
                f'A component with qualifier "{qualifier}" already exists'
            )

        self._components.append(component)

    def _already_exists(self, qualifier: str) -> bool:
        for component in self._components:
            if component.metadata.qualifier == qualifier:
                return True

        return False

    def get_components(self, kind: Type[T]) -> List[Component[T]]:
        return list(
            filter(
                lambda component: component.metadata.kind == kind,
                self._components
            )
        )
