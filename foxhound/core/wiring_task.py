from typing import Any, Callable

from foxhound.core.base_model import BaseModel


class WiringTask(BaseModel):
    target: Callable[..., Any]
    completed: bool = False
