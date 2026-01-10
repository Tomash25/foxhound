from typing import Generic, TypeVar

from pydantic import model_validator

from foxhound.core.base_model import BaseModel

T = TypeVar('T')


class Result(BaseModel, Generic[T]):
    successful: bool
    value: T | None = None
    exception: Exception | None = None

    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        return cls(successful=True, value=value)

    @classmethod
    def fail(cls, exception: Exception) -> 'Result[T]':
        return cls(successful=False, exception=exception)

    @model_validator(mode='after')
    def _check_consistency(self) -> 'Result[T]':
        if self.successful:
            if self.exception is not None:
                raise ValueError('Successful result cannot have an exception')
        else:
            if self.value is not None:
                raise ValueError('Failed result cannot have a value')
        return self
