import os
from functools import cached_property
from typing import Union

import yaml

from foxhound import component

_CONFIGURATION_PATH_ENV_VAR = 'FOXHOUND_CONFIGURATION_PATH'
_DEFAULT_CONFIGURATION_PATH = 'application.yaml'

ConfigurationSection = dict[str, Union[str, 'ConfigurationSection']]


@component()
class ConfigurationReader:
    @cached_property
    def _configuration(self) -> ConfigurationSection:
        if _CONFIGURATION_PATH_ENV_VAR in os.environ:
            configuration_path: str = os.environ[_CONFIGURATION_PATH_ENV_VAR]
        else:
            configuration_path: str = _DEFAULT_CONFIGURATION_PATH

        if not os.path.exists(configuration_path):
            raise FileNotFoundError(
                f'Cannot load configuration file from "{configuration_path}". '
                f'Consider changing {_CONFIGURATION_PATH_ENV_VAR}'
            )

        with open(configuration_path) as f:
            loaded_configuration: ConfigurationSection = yaml.safe_load(f)

        return loaded_configuration if loaded_configuration else ConfigurationSection()

    def read(self, section: str | None) -> ConfigurationSection:
        sections_breakdown: list[str] = [] if section is None else section.split('.')
        target_section: ConfigurationSection = self._configuration

        for next_section in sections_breakdown:
            if next_section in target_section:
                target_section = target_section[next_section]
            else:
                raise KeyError(f'Section "{section}" not found in configuration file')

        return target_section
