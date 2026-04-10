from foxhound.core.parameter import Parameter


class UnsatisfiedDependenciesError(Exception):
    def __init__(self, hints: dict[Parameter, str]):
        self.hints = hints
        listed_hints: str = ''.join([f'\n\t{parameter.name}: {hint}' for parameter, hint in hints.items()])
        super().__init__(f'Dependencies unsatisfied: ' + listed_hints)
