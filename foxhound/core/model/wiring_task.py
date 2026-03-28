from collections.abc import Callable
from typing import Any

from foxhound.core.model.base_model import BaseModel


class WiringTask(BaseModel):
    target: Callable[..., Any]
    completed: bool = False
