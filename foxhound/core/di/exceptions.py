class UnsatisfiedDependenciesError(Exception):
    def __init__(self, missing_parameters_hints: dict[str, str]):
        self.hints = missing_parameters_hints

        listed_hints: str = ''.join([
            f'\n\t{parameter_name}: {hint}'
            for parameter_name, hint in missing_parameters_hints.items()
        ])

        super().__init__('Dependencies unsatisfied' + listed_hints)
