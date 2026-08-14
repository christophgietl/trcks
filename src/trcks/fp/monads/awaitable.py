"""Monadic functions for [collections.abc.Awaitable][].

Provides utilities for functional composition of asynchronous functions.

Example:
    >>> import asyncio
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable as a
    >>> async def read_from_disk() -> str:
    ...     await asyncio.sleep(0.001)
    ...     return "Hello, world!"
    ...
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    ...
    >>> async def write_to_disk(s: str) -> None:
    ...     await asyncio.sleep(0.001)
    ...
    >>> async def main() -> str:
    ...     awaitable_str = read_from_disk()
    ...     return await pipe(
    ...         (
    ...             awaitable_str,
    ...             a.tap(lambda s: print(f"Read '{s}' from disk.")),
    ...             a.map_(transform),
    ...             a.tap_to_awaitable(write_to_disk),
    ...             a.tap(lambda s: print(f"Wrote '{s}' to disk.")),
    ...         ),
    ...     )
    ...
    >>> output = asyncio.run(main())
    Read 'Hello, world!' from disk.
    Wrote 'Length: 13' to disk.
    >>> output
    'Length: 13'
"""

from trcks.fp._monads.awaitable import (
    construct,
    map_,
    map_to_awaitable,
    tap,
    tap_to_awaitable,
    to_coroutine,
)

__all__ = [
    "construct",
    "map_",
    "map_to_awaitable",
    "tap",
    "tap_to_awaitable",
    "to_coroutine",
]
__docformat__ = "google"
