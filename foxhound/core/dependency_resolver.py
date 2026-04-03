from types import GenericAlias

from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.parameter import Parameter
from foxhound.core.model.result import Result
from foxhound.core.typing_tools import is_assignable_to


class DependencyResolver:
    def try_resolve(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        if dependency.qualifier is None:
            return self._find_unqualified_component(dependency, candidates)

        return self._find_qualified_component(dependency, candidates)

    def _find_qualified_component(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        kind: type | GenericAlias = dependency.kind
        qualifier: str = dependency.qualifier

        type_matches: list[ComponentDefinition] = self._filter_matching_candidates(dependency, candidates)

        if len(type_matches) == 0:
            return Result.fail(
                f'No registered component matching {kind} with qualifier "{qualifier}". '
                f'In fact, no component matching {kind} has been found at all.'
            )

        for candidate in type_matches:
            if candidate.metadata.qualifier == qualifier:
                return Result.ok(candidate.metadata.id)

        return Result.fail(
            f'No registered component matching {kind} with qualifier "{qualifier}". '
            f'However, {len(type_matches)} other components matching {kind} are registered.'
        )

    def _find_unqualified_component(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[str]:
        kind: type | GenericAlias = dependency.kind

        type_matches: list[ComponentDefinition] = self._filter_matching_candidates(dependency, candidates)

        if len(type_matches) == 0:
            return Result.fail('No registered component matching {kind}')

        if len(type_matches) == 1:
            return Result.ok(type_matches[0].metadata.id)

        primary_matches: list[ComponentDefinition] = [
            candidate for candidate in type_matches
            if candidate.metadata.primary
        ]

        if len(primary_matches) == 1:
            return Result.ok(primary_matches[0].metadata.id)

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
            dependency: Parameter,
            candidates: list[ComponentDefinition]
    ) -> list[ComponentDefinition]:
        return [
            candidate for candidate in candidates
            if is_assignable_to(candidate.metadata.kind, dependency.kind)
               and candidate.metadata.id != dependency.parent_component_id
        ]
