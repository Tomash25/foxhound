from abc import ABC, abstractmethod
from types import GenericAlias

from foxhound import ComponentDefinition, Result
from foxhound.core.model.parameter import Parameter
from foxhound.core.typing_tools import is_assignable_to


class DependencyResolver(ABC):
    @abstractmethod
    def try_resolve(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        ...


class BasicDependencyResolver(DependencyResolver):
    def try_resolve(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        if dependency.qualifier is None:
            return self._find_unqualified_component(dependency, candidates)

        return self._find_qualified_component(dependency, candidates)

    def _find_qualified_component(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        kind: type | GenericAlias = dependency.kind
        qualifier: str = dependency.qualifier

        type_matches: list[ComponentDefinition] = self._filter_matching_candidates(kind, candidates)

        if len(type_matches) == 0:
            return Result.fail(
                f'No registered component matching {kind} with qualifier "{qualifier}". '
                f'In fact, no component matching {kind} has been found at all.'
            )

        for candidate in type_matches:
            if candidate.component_metadata.qualifier == qualifier:
                return Result.ok(candidate.id)

        return Result.fail(
            f'No registered component matching {kind} with qualifier "{qualifier}". '
            f'However, {len(type_matches)} other components matching {kind} are registered.'
        )

    def _find_unqualified_component(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        kind: type | GenericAlias = dependency.kind

        type_matches: list[ComponentDefinition] = self._filter_matching_candidates(kind, candidates)

        if len(type_matches) == 0:
            return Result.fail('No registered component matching {kind}')

        if len(type_matches) == 1:
            return Result.ok(type_matches[0].id)

        primary_matches: list[ComponentDefinition] = [
            candidate for candidate in type_matches
            if candidate.component_metadata.primary
        ]

        if len(primary_matches) == 1:
            return Result.ok(primary_matches[0].id)

        if len(primary_matches) > 1:
            return Result.fail(
                f'Multiple components matching {kind} were found, '
                f'and multiple of them are marked as primary. '
                f'Specific component can be selected by specifying a qualifier, '
                f'or exactly one primary component.'
            )

        return Result.fail(
            f'Multiple components matching {kind} were found. Specific component '
            f'can be selected by specifying a qualifier or a primary component.'
        )

    def _filter_matching_candidates(
            self,
            kind: type,
            candidates: list[ComponentDefinition]
    ) -> list[ComponentDefinition]:
        return [
            candidate for candidate in candidates
            if is_assignable_to(candidate.component_metadata.kind, kind)
        ]
