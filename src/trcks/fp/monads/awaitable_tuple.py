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
    ...             at.construct_from_tuple((4, 2, 0)),
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
    ...             at.construct_from_tuple((1, 2, 3)),
    ...             at.map_to_awaitable_iterable(slowly_duplicate_integer),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    (1, 1, 2, 2, 3, 3)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, deprecated
from trcks.fp.composition import compose2
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import tuple_ as t

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import AwaitableIterable, AwaitableTuple

__docformat__ = "google"

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def construct(value: _T) -> AwaitableTuple[_T]:
    """Create a [trcks.AwaitableTuple][] from a value.

    Args:
        value: The value to create the [trcks.AwaitableTuple][] from.

    Returns:
        The [trcks.AwaitableTuple][] created from the value.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> a_tpl: AwaitableTuple[int] = at.construct(42)
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (42,)
    """
    return a.construct(t.construct(value))


def construct_from_awaitable(awtbl: Awaitable[_T]) -> AwaitableTuple[_T]:
    """Create a [trcks.AwaitableTuple][] from an awaitable value.

    Args:
        awtbl: The awaitable value to create the [trcks.AwaitableTuple][] from.

    Returns:
        The [trcks.AwaitableTuple][] created from the awaitable value.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> awtbl: Awaitable[int] = a.construct(7)
        >>> a_tpl: AwaitableTuple[int] = at.construct_from_awaitable(awtbl)
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (7,)
    """
    return a.map_(t.construct)(awtbl)


def construct_from_tuple(tpl: tuple[_T, ...]) -> AwaitableTuple[_T]:
    """Create a [trcks.AwaitableTuple][] from a homogeneous tuple.

    Args:
        tpl: The homogeneous tuple to create
            the [trcks.AwaitableTuple][] from.

    Returns:
        The [trcks.AwaitableTuple][] created from the homogeneous tuple.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> a_tpl: AwaitableTuple[int] = at.construct_from_tuple((1, 2))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (1, 2)
    """
    return a.construct(tpl)


def map_(
    f: Callable[[_T1], _T2],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Turn synchronous function into a function
    expecting and returning [trcks.AwaitableTuple][]s
    of the same length.

    Args:
        f:
            The synchronous function to be transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of the same length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of the same length.

    Note:
        The underscore in the function name helps to avoid collisions
        with the built-in function [map][].

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def double_integer(n: int) -> int:
        ...     return n * 2
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2, 3)),
        ...         at.map_(double_integer),
        ...     )
        ... )
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (2, 4, 6)
    """
    return a.map_(t.map_(f))


def map_to_awaitable(
    f: Callable[[_T1], Awaitable[_T2]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Turn [collections.abc.Awaitable][]-returning function into a function
    expecting and returning [trcks.AwaitableTuple][]s
    of the same length.

    Args:
        f:
            The [collections.abc.Awaitable][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableTuple][]s of the same length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of the same length.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_add_one(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n + 1
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2)),
        ...         at.map_to_awaitable(slowly_add_one),
        ...     )
        ... )
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (2, 3)
    """
    return map_to_awaitable_iterable(compose2((f, construct_from_awaitable)))


def map_to_awaitable_iterable(
    f: Callable[[_T1], AwaitableIterable[_T2]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Turn [trcks.AwaitableIterable][]-returning function into a function
    expecting and returning [trcks.AwaitableTuple][]s
    of varying length.

    Args:
        f:
            The [trcks.AwaitableIterable][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_duplicate_integer(n: int) -> tuple[int, int]:
        ...     await asyncio.sleep(0.001)
        ...     return n, n
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2)),
        ...         at.map_to_awaitable_iterable(slowly_duplicate_integer),
        ...     )
        ... )
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (1, 1, 2, 2)
    """

    async def mapped_f(a_t1s: AwaitableTuple[_T1]) -> tuple[_T2, ...]:
        # `tuple` does not support asynchronous generators.
        # Therefore, we need to use a list comprehension and then convert it to a tuple:
        t2s = [t2 for t1 in await a_t1s for t2 in await f(t1)]
        return tuple(t2s)

    return mapped_f


@deprecated("Use map_to_awaitable_iterable instead")
def map_to_awaitable_tuple(
    f: Callable[[_T1], AwaitableTuple[_T2]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.map_to_awaitable_iterable][].
    """
    return map_to_awaitable_iterable(f)  # pragma: no cover


def map_to_iterable(
    f: Callable[[_T1], Iterable[_T2]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Turn [collections.abc.Iterable][]-returning function into a function
    expecting and returning [trcks.AwaitableTuple][]s
    of varying length.

    Args:
        f:
            The [collections.abc.Iterable][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def add_negative(n: int) -> tuple[int, int]:
        ...     return n, -n
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2)),
        ...         at.map_to_iterable(add_negative),
        ...     )
        ... )
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (1, -1, 2, -2)
    """
    return a.map_(t.map_to_iterable(f))


@deprecated("Use map_to_iterable instead")
def map_to_tuple(
    f: Callable[[_T1], tuple[_T2, ...]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Deprecated alias for [trcks.fp.monads.awaitable_tuple.map_to_iterable][]."""
    return map_to_iterable(f)  # pragma: no cover


def tap(
    f: Callable[[_T1], object],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Turn synchronous function into a function
    expecting a [trcks.AwaitableTuple][] and
    returning the same [trcks.AwaitableTuple][].

    Args:
        f:
            The synchronous function to be transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def log_integer(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2)),
        ...         at.tap(log_integer),
        ...     )
        ... )
        >>> tpl = asyncio.run(at.to_coroutine_tuple(a_tpl))
        Received: 1
        Received: 2
        >>> tpl
        (1, 2)
    """
    return a.map_(t.tap(f))


def tap_to_awaitable(
    f: Callable[[_T1], Awaitable[object]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Turn [collections.abc.Awaitable][]-returning function into a function
    expecting a [trcks.AwaitableTuple][] and
    returning the same [trcks.AwaitableTuple][].

    Args:
        f:
            The [collections.abc.Awaitable][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_log_integer(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Received: {n}")
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2)),
        ...         at.tap_to_awaitable(slowly_log_integer),
        ...     )
        ... )
        >>> tpl = asyncio.run(at.to_coroutine_tuple(a_tpl))
        Received: 1
        Received: 2
        >>> tpl
        (1, 2)
    """

    async def bypassed_f(t1: _T1) -> _T1:
        _ = await f(t1)
        return t1

    return map_to_awaitable(bypassed_f)


def tap_to_awaitable_iterable(
    f: Callable[[_T1], AwaitableIterable[object]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Turn a [trcks.AwaitableIterable][]-returning side effect into a function
    expecting a [trcks.AwaitableTuple][] and returning a [trcks.AwaitableTuple][]
    where each original element is repeated once per element returned by
    the side effect.

    Args:
        f:
            The [trcks.AwaitableIterable][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableTuple][] and
            returning a [trcks.AwaitableTuple][] where each original element is
            repeated once per element returned by the side effect.

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning a [trcks.AwaitableTuple][] where each original element is
            repeated once per element returned by the side effect.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_get_divisors(n: int) -> tuple[int, ...]:
        ...     await asyncio.sleep(0.001)
        ...     candidates = range(1, n + 1)
        ...     return tuple(c for c in candidates if n % c == 0)
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2, 3, 4)),
        ...         at.tap_to_awaitable_iterable(slowly_get_divisors),
        ...     )
        ... )
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (1, 2, 2, 3, 3, 4, 4, 4)
    """

    async def bypassed_f(t1: _T1) -> tuple[_T1, ...]:
        objs = await f(t1)
        return tuple(t1 for _ in objs)

    return map_to_awaitable_iterable(bypassed_f)


@deprecated("Use tap_to_awaitable_iterable instead")
def tap_to_awaitable_tuple(
    f: Callable[[_T1], AwaitableTuple[object]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.tap_to_awaitable_iterable][].
    """
    return tap_to_awaitable_iterable(f)  # pragma: no cover


def tap_to_iterable(
    f: Callable[[_T1], Iterable[object]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Turn a [collections.abc.Iterable][]-returning side effect into a function
    expecting a [trcks.AwaitableTuple][] and returning a [trcks.AwaitableTuple][]
    where each original element is repeated once per element returned by
    the side effect.

    Args:
        f:
            The [collections.abc.Iterable][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableTuple][] and
            returning a [trcks.AwaitableTuple][] where each original element is
            repeated once per element returned by the side effect.

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning a [trcks.AwaitableTuple][] where each original element is
            repeated once per element returned by the side effect.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def get_divisors(n: int) -> tuple[int, ...]:
        ...     candidates = range(1, n + 1)
        ...     return tuple(c for c in candidates if n % c == 0)
        >>> a_tpl: AwaitableTuple[int] = pipe(
        ...     (
        ...         at.construct_from_tuple((1, 2, 3, 4)),
        ...         at.tap_to_iterable(get_divisors),
        ...     )
        ... )
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (1, 2, 2, 3, 3, 4, 4, 4)
    """
    return a.map_(t.tap_to_iterable(f))


@deprecated("Use tap_to_iterable instead")
def tap_to_tuple(
    f: Callable[[_T1], tuple[object, ...]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Deprecated alias for [trcks.fp.monads.awaitable_tuple.tap_to_iterable][]."""
    return tap_to_iterable(f)  # pragma: no cover


async def to_coroutine_tuple(a_tpl: AwaitableTuple[_T]) -> tuple[_T, ...]:
    """Turn a [trcks.AwaitableTuple][] into a coroutine.

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        a_tpl: The [trcks.AwaitableTuple][] to be transformed
            into a coroutine.

    Returns:
        The given [trcks.AwaitableTuple][] transformed
            into a coroutine.

    Note:
        The type [trcks.AwaitableTuple][] is
        an alias of [collections.abc.Awaitable][] over
        homogeneous [tuple][] values.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> loop = asyncio.new_event_loop()
        >>> asyncio.set_event_loop(loop)
        >>> future = asyncio.Future[tuple[int, ...]]()
        >>> future.set_result((3, 4))
        >>> future
        <Future finished result=(3, 4)>
        >>> coro = at.to_coroutine_tuple(future)
        >>> coro
        <coroutine object to_coroutine_tuple at 0x...>
        >>> asyncio.run(coro)
        (3, 4)
        >>> loop.close()
    """
    return await a_tpl
