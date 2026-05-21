"""Monadic functions for [trcks.AwaitableTuple][].

Provides utilities for functional composition of
asynchronous [tuple][]-returning functions.

Example:
    Map and tap over an awaitable sequence:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_tuple as as_
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> async def main() -> tuple[int, ...]:
    ...     return await pipe(
    ...         (
    ...             as_.construct_from_tuple((4, 2, 0)),
    ...             as_.map_(double_integer),
    ...             as_.tap(log_integer),
    ...         )
    ...     )
    ...
    >>> sequence = asyncio.run(main())
    Received: 8
    Received: 4
    Received: 0
    >>> sequence
    (8, 4, 0)

    Map each element to an awaitable sequence and flatten the result:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_tuple as as_
    >>> async def slowly_duplicate_integer(n: int) -> tuple[int, int]:
    ...     await asyncio.sleep(0.001)
    ...     return n, n
    ...
    >>> async def main() -> tuple[int, ...]:
    ...     return await pipe(
    ...         (
    ...             as_.construct_from_tuple((1, 2, 3)),
    ...             as_.map_to_awaitable_sequence(slowly_duplicate_integer),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    (1, 1, 2, 2, 3, 3)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.composition import compose2
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import tuple_ as s

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableTuple

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
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> a_seq: AwaitableTuple[int] = as_.construct(42)
        >>> asyncio.run(as_.to_coroutine_tuple(a_seq))
        (42,)
    """
    return a.construct(s.construct(value))


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
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> awtbl: Awaitable[int] = a.construct(7)
        >>> a_seq: AwaitableTuple[int] = as_.construct_from_awaitable(awtbl)
        >>> asyncio.run(as_.to_coroutine_tuple(a_seq))
        (7,)
    """
    return a.map_(s.construct)(awtbl)


def construct_from_tuple(seq: tuple[_T, ...]) -> AwaitableTuple[_T]:
    """Create a [trcks.AwaitableTuple][] from a sequence.

    Args:
        seq: The sequence to create
            the [trcks.AwaitableTuple][] from.

    Returns:
        The [trcks.AwaitableTuple][] created from the sequence.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> a_seq: AwaitableTuple[int] = as_.construct_from_tuple((1, 2))
        >>> asyncio.run(as_.to_coroutine_tuple(a_seq))
        (1, 2)
    """
    return a.construct(seq)


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
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> def double_integer(n: int) -> int:
        ...     return n * 2
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2, 3)),
        ...             as_.map_(double_integer),
        ...         )
        ...     )
        >>> asyncio.run(main())
        (2, 4, 6)
    """
    return a.map_(s.map_(f))


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
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> async def slowly_add_one(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n + 1
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2)),
        ...             as_.map_to_awaitable(slowly_add_one),
        ...         )
        ...     )
        >>> asyncio.run(main())
        (2, 3)
    """
    return map_to_awaitable_sequence(compose2((f, construct_from_awaitable)))


def map_to_awaitable_sequence(
    f: Callable[[_T1], AwaitableTuple[_T2]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Turn [trcks.AwaitableTuple][]-returning function into a function
    expecting and returning [trcks.AwaitableTuple][]s
    of varying length.

    Args:
        f:
            The [trcks.AwaitableTuple][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> async def slowly_duplicate_integer(n: int) -> tuple[int, int]:
        ...     await asyncio.sleep(0.001)
        ...     return n, n
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2)),
        ...             as_.map_to_awaitable_sequence(slowly_duplicate_integer),
        ...         )
        ...     )
        >>> asyncio.run(main())
        (1, 1, 2, 2)
    """

    async def mapped_f(a_t1s: AwaitableTuple[_T1]) -> tuple[_T2, ...]:
        return tuple([t2 for t1 in await a_t1s for t2 in await f(t1)])

    return mapped_f


def map_to_tuple(
    f: Callable[[_T1], tuple[_T2, ...]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Turn sequence-returning function into a function
    expecting and returning [trcks.AwaitableTuple][]s
    of varying length.

    Args:
        f:
            The sequence-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableTuple][]s of varying length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> def add_negative(n: int) -> tuple[int, int]:
        ...     return n, -n
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2)),
        ...             as_.map_to_tuple(add_negative),
        ...         )
        ...     )
        >>> asyncio.run(main())
        (1, -1, 2, -2)
    """
    return a.map_(s.map_to_tuple(f))


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
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> def log_integer(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2)),
        ...             as_.tap(log_integer),
        ...         )
        ...     )
        >>> sequence = asyncio.run(main())
        Received: 1
        Received: 2
        >>> sequence
        (1, 2)
    """
    return a.map_(s.tap(f))


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
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> async def slowly_log_integer(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Received: {n}")
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2)),
        ...             as_.tap_to_awaitable(slowly_log_integer),
        ...         )
        ...     )
        >>> sequence = asyncio.run(main())
        Received: 1
        Received: 2
        >>> sequence
        (1, 2)
    """

    async def bypassed_f(t1: _T1) -> _T1:
        _ = await f(t1)
        return t1

    return map_to_awaitable(bypassed_f)


def tap_to_awaitable_sequence(
    f: Callable[[_T1], AwaitableTuple[object]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Turn [trcks.AwaitableTuple][]-returning function into a function
    expecting a [trcks.AwaitableTuple][] and
    returning the same [trcks.AwaitableTuple][].

    Args:
        f:
            The [trcks.AwaitableTuple][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> async def slowly_get_divisors(n: int) -> tuple[int, ...]:
        ...     await asyncio.sleep(0.001)
        ...     candidates = range(1, n + 1)
        ...     return tuple(c for c in candidates if n % c == 0)
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2, 3, 4)),
        ...             as_.tap_to_awaitable_sequence(slowly_get_divisors),
        ...         )
        ...     )
        >>> asyncio.run(main())
        (1, 2, 2, 3, 3, 4, 4, 4)
    """

    async def bypassed_f(t1: _T1) -> tuple[_T1, ...]:
        objs = await f(t1)
        return tuple(t1 for _ in objs)

    return map_to_awaitable_sequence(bypassed_f)


def tap_to_tuple(
    f: Callable[[_T1], tuple[object, ...]],
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Turn sequence-returning function into a function
    expecting a [trcks.AwaitableTuple][] and
    returning the same [trcks.AwaitableTuple][].

    Args:
        f:
            The sequence-returning function to be transformed
            into a function expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableTuple][] and
            returning the same [trcks.AwaitableTuple][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> def get_divisors(n: int) -> tuple[int, ...]:
        ...     candidates = range(1, n + 1)
        ...     return tuple(c for c in candidates if n % c == 0)
        >>> async def main() -> tuple[int, ...]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_tuple((1, 2, 3, 4)),
        ...             as_.tap_to_tuple(get_divisors),
        ...         )
        ...     )
        >>> asyncio.run(main())
        (1, 2, 2, 3, 3, 4, 4, 4)
    """
    return a.map_(s.tap_to_tuple(f))


async def to_coroutine_tuple(a_seq: AwaitableTuple[_T]) -> tuple[_T, ...]:
    """Turn a [trcks.AwaitableTuple][] into a coroutine.

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        a_seq: The [trcks.AwaitableTuple][] to be transformed
            into a coroutine.

    Returns:
        The given [trcks.AwaitableTuple][] transformed
            into a coroutine.

    Note:
        The type [trcks.AwaitableTuple][] is
        an alias of [collections.abc.Awaitable][] over
        [tuple][] values.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableTuple
        >>> from trcks.fp.monads import awaitable_tuple as as_
        >>> a_seq: AwaitableTuple[int] = as_.construct_from_tuple((3, 4))
        >>> asyncio.run(as_.to_coroutine_tuple(a_seq))
        (3, 4)
    """
    return await a_seq
