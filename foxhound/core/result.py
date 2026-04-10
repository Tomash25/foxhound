from typing import Generic, TypeVar

from foxhound.core.base_model import BaseModel

T = TypeVar('T')


class Result(BaseModel, Generic[T]):
    successful: bool
    value: T | None = None
    exception: Exception | None = None
    hint: str | None = None

    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        return cls(successful=True, value=value)

    @classmethod
    def fail(cls, hint: str | None = None) -> 'Result[T]':
        return cls(successful=False, hint=hint)

    @classmethod
    def incomplete(cls, value: T, exception: Exception | None, hint: str | None = None) -> 'Result[T]':
        return cls(successful=False, value=value, exception=exception, hint=hint)

    @classmethod
    def bad(cls, value: T, exception: Exception | None, hint: str | None = None) -> 'Result[T]':
        return cls(successful=False, value=value, exception=exception, hint=hint)

    @classmethod
    def error(cls, exception: Exception, hint: str | None = None) -> 'Result[T]':
        return cls(successful=False, exception=exception, hint=hint)
