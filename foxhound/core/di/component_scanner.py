import importlib
import inspect
import pkgutil
from collections.abc import Iterator
from types import ModuleType

from foxhound.core.di.consts import OBJECT_COMPONENT_DEFINITION_ATTRIBUTE
from foxhound.core.di.models import ComponentDefinition


class ComponentScanner:
    def __init__(self, module: str):
        self._module = module

    def scan(self) -> list[ComponentDefinition]:
        definitions: list[ComponentDefinition] = []
        package: ModuleType = importlib.import_module(self._module)
        module_iterator: Iterator[pkgutil.ModuleInfo] = pkgutil.walk_packages(
            path=package.__path__,
            prefix=package.__name__ + '.',
            onerror=lambda _: None
        )

        for _, module_name, _ in module_iterator:
            module: ModuleType = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module):
                definition: ComponentDefinition | None = getattr(obj, OBJECT_COMPONENT_DEFINITION_ATTRIBUTE, None)
                if definition is not None:
                    definitions.append(definition)

        return definitions
