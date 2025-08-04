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

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.monads import identity as i

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

__docformat__ = "google"

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


async def _construct(value: _T) -> _T:
    return value


def construct(value: _T) -> Awaitable[_T]:
    """Create a [collections.abc.Awaitable][] from a value.

    Args:
        value: The value to create the [collections.abc.Awaitable][] from.

    Returns:
        The [collections.abc.Awaitable][] created from the value.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> awtbl = a.construct("Hello, world!")
        >>> isinstance(awtbl, Awaitable)
        True
        >>> asyncio.run(a.to_coroutine(awtbl))
        'Hello, world!'
    """
    return _construct(value)


def map_(f: Callable[[_T1], _T2]) -> Callable[[Awaitable[_T1]], Awaitable[_T2]]:
    """Turn synchronous function into a function
    expecting and returning [collections.abc.Awaitable][].

    Args:
        f:
            The synchronous function to be transformed into
            a function expecting and returning a [collections.abc.Awaitable][].

    Returns:
        The given function transformed into
            a function expecting and returning a [collections.abc.Awaitable][].

    Note:
        The underscore in the function name helps to avoid collisions
        with the built-in function [map][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> def transform(s: str) -> str:
        ...     return f"Length: {len(s)}"
        ...
        >>> transform_mapped = a.map_(transform)
        >>> awaitable_input = a.construct("Hello, world!")
        >>> awaitable_output = transform_mapped(awaitable_input)
        >>> isinstance(awaitable_output, Awaitable)
        True
        >>> asyncio.run(a.to_coroutine(awaitable_output))
        'Length: 13'

    """

    def composed_f(value: _T1) -> Awaitable[_T2]:
        return construct(f(value))

    return map_to_awaitable(composed_f)


def map_to_awaitable(
    f: Callable[[_T1], Awaitable[_T2]],
) -> Callable[[Awaitable[_T1]], Awaitable[_T2]]:
    """Turn [collections.abc.Awaitable][]-returning function into
    function expecting and returning [collections.abc.Awaitable][].

    Args:
        f:
            The [collections.abc.Awaitable][]-returning function to be transformed into
            a function expecting and returning a [collections.abc.Awaitable][].

    Returns:
        The given function transformed into
            a function expecting and returning a [collections.abc.Awaitable][].


    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> async def write_to_disk(output: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{output}' to disk.")
        ...
        >>> write_to_disk_mapped = a.map_to_awaitable(write_to_disk)
        >>> awaitable_input = a.construct("Hello, world!")
        >>> awaitable_output = write_to_disk_mapped(awaitable_input)
        >>> isinstance(awaitable_output, Awaitable)
        True
        >>> asyncio.run(a.to_coroutine(awaitable_output))
        Wrote 'Hello, world!' to disk.
    """

    async def mapped_f(awaitable: Awaitable[_T1]) -> _T2:
        return await f(await awaitable)

    return mapped_f


def tap(f: Callable[[_T1], object]) -> Callable[[Awaitable[_T1]], Awaitable[_T1]]:
    """Turn synchronous function into a function
    expecting a [collections.abc.Awaitable][] and
    returning the same [collections.abc.Awaitable][].

    Args:
        f:
            The synchronous function to be transformed into a function
            expecting a [collections.abc.Awaitable][] and
            returning the same [collections.abc.Awaitable][].

    Returns:
        The given function transformed into a function
            expecting a [collections.abc.Awaitable][] and
            returning the same [collections.abc.Awaitable][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> def print_string(s: str) -> None:
        ...     print(f"String: {s}")
        ...
        >>> print_string_tapped = a.tap(print_string)
        >>> awaitable_input = a.construct("Hello, world!")
        >>> awaitable_output = print_string_tapped(awaitable_input)
        >>> isinstance(awaitable_output, Awaitable)
        True
        >>> value = asyncio.run(a.to_coroutine(awaitable_output))
        String: Hello, world!
        >>> value
        'Hello, world!'
    """
    return map_(i.tap(f))


def tap_to_awaitable(
    f: Callable[[_T1], Awaitable[object]],
) -> Callable[[Awaitable[_T1]], Awaitable[_T1]]:
    """Turn [collections.abc.Awaitable][]-returning function into a function
    expecting a [collections.abc.Awaitable][] and
    returning the same [collections.abc.Awaitable][].

    Args:
        f:
            The asynchronous function to be transformed into a function
            expecting a [collections.abc.Awaitable][] and
            returning the same [collections.abc.Awaitable][].

    Returns:
        The given function transformed into a function
            expecting a [collections.abc.Awaitable][] and
            returning the same [collections.abc.Awaitable][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> async def write_to_disk(output: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{output}' to disk.")
        ...
        >>> write_to_disk_tapped = a.tap_to_awaitable(write_to_disk)
        >>> awaitable_input = a.construct("Hello, world!")
        >>> awaitable_output = write_to_disk_tapped(awaitable_input)
        >>> isinstance(awaitable_output, Awaitable)
        True
        >>> value = asyncio.run(a.to_coroutine(awaitable_output))
        Wrote 'Hello, world!' to disk.
        >>> value
        'Hello, world!'
    """

    async def bypassed_f(value: _T1) -> _T1:
        _ = await f(value)
        return value

    return map_to_awaitable(bypassed_f)


async def to_coroutine(awtbl: Awaitable[_T]) -> _T:
    """Turn a [collections.abc.Awaitable][] into a [collections.abc.Coroutine][].

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        awtbl: The [collections.abc.Awaitable][] to be transformed
            into a [collections.abc.Coroutine][].

    Returns:
        The given [collections.abc.Awaitable][] transformed
            into a [collections.abc.Coroutine][].

    Note:
        The type [collections.abc.Awaitable][] is
        a supertype of [collections.abc.Coroutine][].

    Example:
        Transform an [asyncio.Future][] into a [collections.abc.Coroutine][] and run it:

        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> asyncio.set_event_loop(asyncio.new_event_loop())
        >>> future = asyncio.Future[str]()
        >>> future.set_result("Hello, world!")
        >>> future
        <Future finished result='Hello, world!'>
        >>> coro = a.to_coroutine(future)
        >>> coro
        <coroutine object to_coroutine at 0x...>
        >>> asyncio.run(coro)
        'Hello, world!'
    """
    return await awtbl
