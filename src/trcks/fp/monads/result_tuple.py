"""Monadic functions for [trcks.ResultTuple][].

Provides utilities for functional composition of
functions returning [trcks.ResultTuple][] values.

Example:
    Map and tap each element inside a success tuple:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result_tuple as rt
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> result_tuple = pipe(
    ...     (
    ...         rt.construct_successes_from_iterable((1, 2, 3)),
    ...         rt.map_successes(double_integer),
    ...         rt.tap_successes(log_integer),
    ...         rt.map_successes_to_iterable(duplicate_integer),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> result_tuple
    ('success', (2, 2, 4, 4, 6, 6))
"""

from trcks.fp._monads.result_tuple import (
    construct_failure,
    construct_from_result,
    construct_from_result_iterable,
    construct_successes,
    construct_successes_from_iterable,
    construct_successes_from_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_failure,
    map_failure_to_iterable,
    map_failure_to_result,
    map_failure_to_result_iterable,
    map_failure_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_failure_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_successes,
    map_successes_to_iterable,
    map_successes_to_result,
    map_successes_to_result_iterable,
    map_successes_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_successes_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_failure,
    tap_failure_to_iterable,
    tap_failure_to_result,
    tap_failure_to_result_iterable,
    tap_failure_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_failure_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_successes,
    tap_successes_to_iterable,
    tap_successes_to_result,
    tap_successes_to_result_iterable,
    tap_successes_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_successes_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
)

__all__ = [
    "construct_failure",
    "construct_from_result",
    "construct_from_result_iterable",
    "construct_successes",
    "construct_successes_from_iterable",
    "construct_successes_from_tuple",
    "map_failure",
    "map_failure_to_iterable",
    "map_failure_to_result",
    "map_failure_to_result_iterable",
    "map_failure_to_result_tuple",
    "map_failure_to_tuple",
    "map_successes",
    "map_successes_to_iterable",
    "map_successes_to_result",
    "map_successes_to_result_iterable",
    "map_successes_to_result_tuple",
    "map_successes_to_tuple",
    "tap_failure",
    "tap_failure_to_iterable",
    "tap_failure_to_result",
    "tap_failure_to_result_iterable",
    "tap_failure_to_result_tuple",
    "tap_failure_to_tuple",
    "tap_successes",
    "tap_successes_to_iterable",
    "tap_successes_to_result",
    "tap_successes_to_result_iterable",
    "tap_successes_to_result_tuple",
    "tap_successes_to_tuple",
]
__docformat__ = "google"
