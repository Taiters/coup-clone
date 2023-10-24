from typing import Optional, TypeVar

T = TypeVar("T")


def not_null(input: Optional[T]) -> T:
    if input is None:
        raise Exception("Unexpected null value")
    return input
