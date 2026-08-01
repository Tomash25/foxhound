import importlib
import pkgutil
import sys
from types import ModuleType

from foxhound.core.di.consts import OBJECT_COMPONENT_DEFINITION_ATTRIBUTE
from foxhound.core.di.models import ComponentDefinition


class ComponentScanner:
    def scan(self, modules: set[str | ModuleType]) -> list[ComponentDefinition]:
        seen: set[str] = set()
        definitions: list[ComponentDefinition] = []

        for module in self._resolve_modules(modules):
            for definition in self._collect_from_module(module):
                if definition.metadata.id in seen:
                    continue

                seen.add(definition.metadata.id)
                definitions.append(definition)

        return definitions

    def _resolve_modules(self, roots: set[str | ModuleType]) -> list[ModuleType]:
        modules: dict[str, ModuleType] = {}

        for root in roots:
            module: ModuleType = importlib.import_module(root) if isinstance(root, str) else root
            modules[module.__name__] = module

            is_package: bool = hasattr(module, '__path__')

            if is_package:
                for _, submodule_name, _ in pkgutil.walk_packages(module.__path__, prefix=f'{module.__name__}.'):
                    modules[submodule_name] = sys.modules.get(submodule_name) or importlib.import_module(submodule_name)

        return list(modules.values())

    def _collect_from_module(self, module: ModuleType) -> list[ComponentDefinition]:
        return [
            definition for obj in vars(module).values()
            if type(definition := getattr(obj, OBJECT_COMPONENT_DEFINITION_ATTRIBUTE, None)) is ComponentDefinition
        ]
