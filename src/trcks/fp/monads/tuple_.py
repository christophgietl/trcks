"""Monadic functions for homogeneous [tuple][]s.

Provides utilities for functional composition of functions
returning homogeneous [tuple][] values.

Note:
    The underscore in the module name helps to avoid collisions
    with the built-in class [tuple][].

Example:
    Create and process a homogeneous [tuple][]:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import tuple_ as t
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> tpl = pipe(
    ...     (
    ...         (1, 2, 3),
    ...         t.map_(double_integer),
    ...         t.tap(log_integer),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> tpl
    (2, 4, 6)

    Map each element to a homogeneous tuple and flatten the result:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import tuple_ as t
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> tpl = pipe(
    ...     (
    ...         (1, 2, 3),
    ...         t.map_to_iterable(duplicate_integer),
    ...     )
    ... )
    >>> tpl
    (1, 1, 2, 2, 3, 3)
"""

from trcks.fp._monads.tuple_ import (
    construct,
    map_,
    map_to_iterable,
    map_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap,
    tap_to_iterable,
    tap_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
)

__all__ = [
    "construct",
    "map_",
    "map_to_iterable",
    "map_to_tuple",
    "tap",
    "tap_to_iterable",
    "tap_to_tuple",
]
__docformat__ = "google"
