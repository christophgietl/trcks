"""Monadic functions for [trcks.AwaitableResultTuple][].

Provides utilities for functional composition of
asynchronous [trcks.ResultTuple][]-returning functions.

Example:
    Map and tap each element inside an awaitable success tuple:

    >>> import asyncio
    >>> from trcks import Result
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_result_tuple as art
    >>> async def slowly_read_from_disk() -> Result[str, int]:
    ...     await asyncio.sleep(0.001)
    ...     return "success", 3
    ...
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> async def main() -> Result[str, tuple[int, ...]]:
    ...     return await pipe(
    ...         (
    ...             art.construct_from_awaitable_result(slowly_read_from_disk()),
    ...             art.map_successes(double_integer),
    ...             art.tap_successes(log_integer),
    ...             art.map_successes_to_iterable(duplicate_integer),
    ...         )
    ...     )
    ...
    >>> r_tpl = asyncio.run(main())
    Received: 6
    >>> r_tpl
    ('success', (6, 6))
"""

from __future__ import annotations

from trcks.fp._monads.awaitable_result_tuple import (
    construct_failure,
    construct_failure_from_awaitable,
    construct_from_awaitable_result,
    construct_from_awaitable_result_iterable,
    construct_from_result,
    construct_from_result_iterable,
    construct_from_result_tuple,
    construct_successes,
    construct_successes_from_awaitable,
    construct_successes_from_awaitable_iterable,
    construct_successes_from_iterable,
    construct_successes_from_tuple,
    map_failure,
    map_failure_to_awaitable,
    map_failure_to_awaitable_iterable,
    map_failure_to_awaitable_result,
    map_failure_to_awaitable_result_iterable,
    map_failure_to_awaitable_result_tuple,
    map_failure_to_awaitable_tuple,
    map_failure_to_iterable,
    map_failure_to_result,
    map_failure_to_result_iterable,
    map_failure_to_result_tuple,
    map_failure_to_tuple,
    map_successes,
    map_successes_to_awaitable,
    map_successes_to_awaitable_iterable,
    map_successes_to_awaitable_result,
    map_successes_to_awaitable_result_iterable,
    map_successes_to_awaitable_result_tuple,
    map_successes_to_awaitable_tuple,
    map_successes_to_iterable,
    map_successes_to_result,
    map_successes_to_result_iterable,
    map_successes_to_result_tuple,
    map_successes_to_tuple,
    tap_failure,
    tap_failure_to_awaitable,
    tap_failure_to_awaitable_iterable,
    tap_failure_to_awaitable_result,
    tap_failure_to_awaitable_result_iterable,
    tap_failure_to_awaitable_result_tuple,
    tap_failure_to_awaitable_tuple,
    tap_failure_to_iterable,
    tap_failure_to_result,
    tap_failure_to_result_iterable,
    tap_failure_to_result_tuple,
    tap_failure_to_tuple,
    tap_successes,
    tap_successes_to_awaitable,
    tap_successes_to_awaitable_iterable,
    tap_successes_to_awaitable_result,
    tap_successes_to_awaitable_result_iterable,
    tap_successes_to_awaitable_result_tuple,
    tap_successes_to_awaitable_tuple,
    tap_successes_to_iterable,
    tap_successes_to_result,
    tap_successes_to_result_iterable,
    tap_successes_to_result_tuple,
    tap_successes_to_tuple,
    to_coroutine_result_tuple,
)

__all__ = [
    "construct_failure",
    "construct_failure_from_awaitable",
    "construct_from_awaitable_result",
    "construct_from_awaitable_result_iterable",
    "construct_from_result",
    "construct_from_result_iterable",
    "construct_from_result_tuple",
    "construct_successes",
    "construct_successes_from_awaitable",
    "construct_successes_from_awaitable_iterable",
    "construct_successes_from_iterable",
    "construct_successes_from_tuple",
    "map_failure",
    "map_failure_to_awaitable",
    "map_failure_to_awaitable_iterable",
    "map_failure_to_awaitable_result",
    "map_failure_to_awaitable_result_iterable",
    "map_failure_to_awaitable_result_tuple",
    "map_failure_to_awaitable_tuple",
    "map_failure_to_iterable",
    "map_failure_to_result",
    "map_failure_to_result_iterable",
    "map_failure_to_result_tuple",
    "map_failure_to_tuple",
    "map_successes",
    "map_successes_to_awaitable",
    "map_successes_to_awaitable_iterable",
    "map_successes_to_awaitable_result",
    "map_successes_to_awaitable_result_iterable",
    "map_successes_to_awaitable_result_tuple",
    "map_successes_to_awaitable_tuple",
    "map_successes_to_iterable",
    "map_successes_to_result",
    "map_successes_to_result_iterable",
    "map_successes_to_result_tuple",
    "map_successes_to_tuple",
    "tap_failure",
    "tap_failure_to_awaitable",
    "tap_failure_to_awaitable_iterable",
    "tap_failure_to_awaitable_result",
    "tap_failure_to_awaitable_result_iterable",
    "tap_failure_to_awaitable_result_tuple",
    "tap_failure_to_awaitable_tuple",
    "tap_failure_to_iterable",
    "tap_failure_to_result",
    "tap_failure_to_result_iterable",
    "tap_failure_to_result_tuple",
    "tap_failure_to_tuple",
    "tap_successes",
    "tap_successes_to_awaitable",
    "tap_successes_to_awaitable_iterable",
    "tap_successes_to_awaitable_result",
    "tap_successes_to_awaitable_result_iterable",
    "tap_successes_to_awaitable_result_tuple",
    "tap_successes_to_awaitable_tuple",
    "tap_successes_to_iterable",
    "tap_successes_to_result",
    "tap_successes_to_result_iterable",
    "tap_successes_to_result_tuple",
    "tap_successes_to_tuple",
    "to_coroutine_result_tuple",
]
__docformat__ = "google"

# Re-assign __module__ to match the facade module name for test compatibility
for _name in __all__:
    if _name.startswith(("map", "tap")):
        globals()[_name].__module__ = __name__
