import typing
from types import GenericAlias

from foxhound.core.di.models import ComponentDefinition, Parameter
from foxhound.core.models import Result
from foxhound.core.utils.typing import is_assignable_to


class DependencyResolver:
    def try_resolve(self, dependency: Parameter, candidates: list[ComponentDefinition]) -> Result[list[str]]:
        if dependency.qualifier is None:
            return self._find_unqualified_components(dependency, candidates)

        return self._find_qualified_component(dependency, candidates)

    def _find_qualified_component(
            self,
            dependency: Parameter,
            candidates: list[ComponentDefinition]
    ) -> Result[list[str]]:
        kind: type | GenericAlias = dependency.kind
        qualifier: str = dependency.qualifier

        type_matches: list[ComponentDefinition] = self._filter_matching_candidates(
            kind,
            dependency.parent_component_id,
            candidates
        )

        if len(type_matches) == 0:
            return Result.fail(
                f'No registered component matching {kind} with qualifier "{qualifier}". '
                f'In fact, no component matching {kind} has been found at all.'
            )

        for candidate in type_matches:
            if candidate.metadata.qualifier == qualifier:
                return Result.ok([candidate.metadata.id])

        return Result.fail(
            f'No registered component matching {kind} with qualifier "{qualifier}". '
            f'However, {len(type_matches)} other components matching {kind} are registered.'
        )

    def _find_unqualified_components(
            self,
            dependency: Parameter,
            candidates: list[ComponentDefinition]
    ) -> Result[list[str]]:
        kind: type | GenericAlias = dependency.kind

        type_matches: list[ComponentDefinition] = self._filter_matching_candidates(
            kind,
            dependency.parent_component_id,
            candidates
        )

        if len(type_matches) == 0:
            if typing.get_origin(kind) is list:
                subtype_matches: list[ComponentDefinition] = self._filter_matching_candidates(
                    typing.get_args(kind)[0],
                    dependency.parent_component_id,
                    candidates
                )

                return Result.ok([component.metadata.id for component in subtype_matches])

            return Result.fail(f'No registered component matching {kind}')

        if len(type_matches) == 1:
            return Result.ok([type_matches[0].metadata.id])

        primary_matches: list[ComponentDefinition] = [
            candidate for candidate in type_matches
            if candidate.metadata.primary
        ]

        if len(primary_matches) == 1:
            return Result.ok([primary_matches[0].metadata.id])

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
            kind: type | GenericAlias,
            parent_component_id: str,
            candidates: list[ComponentDefinition]
    ) -> list[ComponentDefinition]:
        return [
            candidate for candidate in candidates
            if is_assignable_to(candidate.metadata.kind, kind)
               and candidate.metadata.id != parent_component_id
        ]
