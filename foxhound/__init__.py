"""
Foxhound - A lightweight dependency injection framework for Python.
"""

from foxhound.core.di.api import component, define_component, start
from foxhound.core.di.component import Component
from foxhound.core.di.component_definition import ComponentDefinition
from foxhound.core.di.component_metadata import ComponentMetadata
from foxhound.core.di.container import Container
from foxhound.core.result import Result

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
