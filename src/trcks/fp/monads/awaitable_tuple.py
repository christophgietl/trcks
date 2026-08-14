"""Monadic functions for [trcks.AwaitableTuple][].

Provides utilities for functional composition of
asynchronous homogeneous-[tuple][]-returning functions.

Example:
    Map and tap over an awaitable homogeneous tuple:

    >>> import asyncio
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_tuple as at
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> async def main() -> tuple[int, ...]:
    ...     return await pipe(
    ...         (
    ...             at.construct_from_iterable((4, 2, 0)),
    ...             at.map_(double_integer),
    ...             at.tap(log_integer),
    ...         )
    ...     )
    ...
    >>> tpl = asyncio.run(main())
    Received: 8
    Received: 4
    Received: 0
    >>> tpl
    (8, 4, 0)

    Map each element to an awaitable homogeneous tuple and flatten the result:

    >>> import asyncio
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_tuple as at
    >>> async def slowly_duplicate_integer(n: int) -> tuple[int, int]:
    ...     await asyncio.sleep(0.001)
    ...     return n, n
    ...
    >>> async def main() -> tuple[int, ...]:
    ...     return await pipe(
    ...         (
    ...             at.construct_from_iterable((1, 2, 3)),
    ...             at.map_to_awaitable_iterable(slowly_duplicate_integer),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    (1, 1, 2, 2, 3, 3)
"""

from trcks.fp._monads.awaitable_tuple import (
    construct,
    construct_from_awaitable,
    construct_from_awaitable_iterable,
    construct_from_iterable,
    construct_from_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_,
    map_to_awaitable,
    map_to_awaitable_iterable,
    map_to_awaitable_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_to_iterable,
    map_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap,
    tap_to_awaitable,
    tap_to_awaitable_iterable,
    tap_to_awaitable_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_to_iterable,
    tap_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    to_coroutine_tuple,
)

__all__ = [
    "construct",
    "construct_from_awaitable",
    "construct_from_awaitable_iterable",
    "construct_from_iterable",
    "construct_from_tuple",
    "map_",
    "map_to_awaitable",
    "map_to_awaitable_iterable",
    "map_to_awaitable_tuple",
    "map_to_iterable",
    "map_to_tuple",
    "tap",
    "tap_to_awaitable",
    "tap_to_awaitable_iterable",
    "tap_to_awaitable_tuple",
    "tap_to_iterable",
    "tap_to_tuple",
    "to_coroutine_tuple",
]
__docformat__ = "google"
