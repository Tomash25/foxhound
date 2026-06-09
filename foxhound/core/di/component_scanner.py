import sys
from types import ModuleType
from typing import Any

from foxhound.core.di.consts import OBJECT_COMPONENT_DEFINITION_ATTRIBUTE
from foxhound.core.di.models import ComponentDefinition


class ComponentScanner:
    def scan(self) -> list[ComponentDefinition]:
        seen: set[str] = set()
        definitions: list[ComponentDefinition] = []

        for module in list(sys.modules.values()):
            if module is None:
                continue

            module_definitions: list[ComponentDefinition] = self._collect_from_module(module)

            for definition in module_definitions:
                if definition.metadata.id in seen:
                    continue

                seen.add(definition.metadata.id)
                definitions.append(definition)

        return definitions

    def _collect_from_module(self, module: ModuleType) -> list[ComponentDefinition]:
        collected_definitions: list[ComponentDefinition] = []
        module_members: list[Any] = list(vars(module).values())

        for obj in module_members:
            definition: ComponentDefinition | None = getattr(obj, OBJECT_COMPONENT_DEFINITION_ATTRIBUTE, None)

            if type(definition) is ComponentDefinition:
                collected_definitions.append(definition)

        return collected_definitions
