"""Functions for the identity monad.

Provides utilities for functional composition of synchronous functions.
"""

from collections.abc import Callable
from typing import TypeVar

__docformat__ = "google"

_T = TypeVar("_T")


def tap(f: Callable[[_T], object]) -> Callable[[_T], _T]:
    """Turn synchronous function into a function that returns its input.

    Args:
        f:
            The synchronous function to be transformed into
            a function that returns its input.

    Returns:
        The given function transformed into a function that returns its input.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks.fp.monads import identity as i
        >>> log_and_pass_on: Callable[[object], object] = i.tap(
        ...     lambda o: print(f"Received object {o}.")
        ... )
        >>> output = log_and_pass_on(42)
        Received object 42.
        >>> output
        42
    """

    def bypassed_f(value: _T) -> _T:
        _ = f(value)
        return value

    return bypassed_f
