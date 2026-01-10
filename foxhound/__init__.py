"""
Foxhound - A lightweight dependency injection framework for Python.
"""

from foxhound.core.api import component, define_component, start, wire
from foxhound.core.component import Component
from foxhound.core.component_definition import ComponentDefinition
from foxhound.core.component_metadata import ComponentMetadata
from foxhound.core.container import Container
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
