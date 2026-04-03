"""
Foxhound - A lightweight dependency injection framework for Python.
"""

from foxhound.core.api import component, define_component, start
from foxhound.core.model.component import Component
from foxhound.core.model.component_definition import ComponentDefinition
from foxhound.core.model.component_metadata import ComponentMetadata
from foxhound.core.container import Container
from foxhound.core.model.result import Result

__version__ = '0.1.0'

__all__ = [
    'component',
    'define_component',
    'start',
    'wire',
    'Component',
    'ComponentDefinition',
    'ComponentMetadata',
    'Container',
    'Result',
]
