"""Monadic functions for [trcks.AwaitableResult][].

Provides utilities for functional composition of
asynchronous [trcks.Result][]-returning functions.

Example:
    >>> import asyncio
    >>> import math
    >>> from trcks import Result
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_result as ar
    >>> async def read_from_disk() -> Result[str, float]:
    ...     await asyncio.sleep(0.001)
    ...     return "failure", "not found"
    ...
    >>> def get_square_root(x: float) -> Result[str, float]:
    ...     if x < 0:
    ...         return "failure", "negative value"
    ...     return "success", math.sqrt(x)
    ...
    >>> async def write_to_disk(output: float) -> None:
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{output}' to disk.")
    ...
    >>> async def main() -> Result[str, float]:
    ...     a_rslt = read_from_disk()
    ...     return await pipe(
    ...         (
    ...             a_rslt,
    ...             ar.map_success_to_result(get_square_root),
    ...             ar.tap_success_to_awaitable(write_to_disk),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    ('failure', 'not found')
"""

from __future__ import annotations

from trcks.fp._monads.awaitable_result import (
    construct_failure,
    construct_failure_from_awaitable,
    construct_from_result,
    construct_success,
    construct_success_from_awaitable,
    map_failure,
    map_failure_to_awaitable,
    map_failure_to_awaitable_result,
    map_failure_to_result,
    map_success,
    map_success_to_awaitable,
    map_success_to_awaitable_result,
    map_success_to_result,
    tap_failure,
    tap_failure_to_awaitable,
    tap_failure_to_awaitable_result,
    tap_failure_to_result,
    tap_success,
    tap_success_to_awaitable,
    tap_success_to_awaitable_result,
    tap_success_to_result,
    to_coroutine_result,
)

__all__ = [
    "construct_failure",
    "construct_failure_from_awaitable",
    "construct_from_result",
    "construct_success",
    "construct_success_from_awaitable",
    "map_failure",
    "map_failure_to_awaitable",
    "map_failure_to_awaitable_result",
    "map_failure_to_result",
    "map_success",
    "map_success_to_awaitable",
    "map_success_to_awaitable_result",
    "map_success_to_result",
    "tap_failure",
    "tap_failure_to_awaitable",
    "tap_failure_to_awaitable_result",
    "tap_failure_to_result",
    "tap_success",
    "tap_success_to_awaitable",
    "tap_success_to_awaitable_result",
    "tap_success_to_result",
    "to_coroutine_result",
]
__docformat__ = "google"

# Re-assign __module__ to match the facade module name for test compatibility
for _name in __all__:
    if _name.startswith(("map", "tap")):
        globals()[_name].__module__ = __name__
