"""
Foxhound - A lightweight dependency injection framework for Python.
"""

from foxhound.core.di.api import component, define_component, start
from foxhound.core.di.container import Container
from foxhound.core.di.models import Component, ComponentDefinition, ComponentMetadata
from foxhound.core.models import Result

__version__ = '0.1.4'

__all__ = [
    'component',
    'define_component',
    'start',
    'Component',
    'ComponentDefinition',
    'ComponentMetadata',
    'Container',
    'Result',
]
