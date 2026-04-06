"""Monadic functions for [trcks.AwaitableSequence][].

Provides utilities for functional composition of
asynchronous [collections.abc.Sequence][]-returning functions.

Example:
    Map and tap over an awaitable sequence:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_sequence as as_
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> async def main() -> Sequence[int]:
    ...     return await pipe(
    ...         (
    ...             as_.construct_from_sequence([4, 2, 0]),
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
    [8, 4, 0]

    Map each element to an awaitable sequence and flatten the result:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_sequence as as_
    >>> async def duplicate_integer(n: int) -> list[int]:
    ...     await asyncio.sleep(0.001)
    ...     return [n, n]
    ...
    >>> async def main() -> Sequence[int]:
    ...     return await pipe(
    ...         (
    ...             as_.construct_from_sequence([1, 2, 3]),
    ...             as_.map_to_awaitable_sequence(duplicate_integer),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    [1, 1, 2, 2, 3, 3]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.composition import compose2
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import sequence as s

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable, Sequence

    from trcks import AwaitableSequence

__docformat__ = "google"

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def construct(value: _T) -> AwaitableSequence[_T]:
    """Create a [trcks.AwaitableSequence][] from a value.

    Args:
        value: The value to create the [trcks.AwaitableSequence][] from.

    Returns:
        The [trcks.AwaitableSequence][] created from the value.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableSequence
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> a_seq: AwaitableSequence[int] = as_.construct(42)
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [42]
    """
    return a.construct(s.construct(value))


def construct_from_awaitable(awtbl: Awaitable[_T]) -> AwaitableSequence[_T]:
    """Create a [trcks.AwaitableSequence][] from an awaitable value.

    Args:
        awtbl: The awaitable value to create the [trcks.AwaitableSequence][] from.

    Returns:
        The [trcks.AwaitableSequence][] created from the awaitable value.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable, Sequence
        >>> from trcks import AwaitableSequence
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> awtbl: Awaitable[int] = a.construct(7)
        >>> a_seq: AwaitableSequence[int] = as_.construct_from_awaitable(awtbl)
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [7]
    """
    return a.map_(s.construct)(awtbl)


def construct_from_sequence(seq: Sequence[_T]) -> AwaitableSequence[_T]:
    """Create a [trcks.AwaitableSequence][] from a [collections.abc.Sequence][].

    Args:
        seq: The [collections.abc.Sequence][] to create
            the [trcks.AwaitableSequence][] from.

    Returns:
        The [trcks.AwaitableSequence][] created from the sequence.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks import AwaitableSequence
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> a_seq: AwaitableSequence[int] = as_.construct_from_sequence([1, 2])
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [1, 2]
    """
    return a.construct(seq)


def map_(
    f: Callable[[_T1], _T2],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Turn synchronous function into a function
    expecting and returning [trcks.AwaitableSequence][]s
    of the same length.

    Args:
        f:
            The synchronous function to be transformed into
            a function expecting and returning
            [trcks.AwaitableSequence][]s of the same length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableSequence][]s of the same length.

    Note:
        The underscore in the function name helps to avoid collisions
        with the built-in function [map][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2, 3]),
        ...             as_.map_(lambda n: n * 2),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [2, 4, 6]
    """
    return a.map_(s.map_(f))


def map_to_awaitable(
    f: Callable[[_T1], Awaitable[_T2]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Turn [collections.abc.Awaitable][]-returning function into a function
    expecting and returning [trcks.AwaitableSequence][]s
    of the same length.

    Args:
        f:
            The [collections.abc.Awaitable][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableSequence][]s of the same length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableSequence][]s of the same length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def add_one(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n + 1
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.map_to_awaitable(add_one),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [2, 3]
    """
    return map_to_awaitable_sequence(compose2((f, construct_from_awaitable)))


def map_to_awaitable_sequence(
    f: Callable[[_T1], AwaitableSequence[_T2]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Turn [trcks.AwaitableSequence][]-returning function into a function
    expecting and returning [trcks.AwaitableSequence][]s
    of varying length.

    Args:
        f:
            The [trcks.AwaitableSequence][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableSequence][]s of varying length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableSequence][]s of varying length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def duplicate_integer(n: int) -> list[int]:
        ...     await asyncio.sleep(0.001)
        ...     return [n, n]
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.map_to_awaitable_sequence(duplicate_integer),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [1, 1, 2, 2]
    """

    async def mapped_f(a_t1s: AwaitableSequence[_T1]) -> Sequence[_T2]:
        return [t2 for t1 in await a_t1s for t2 in await f(t1)]

    return mapped_f


def map_to_sequence(
    f: Callable[[_T1], Sequence[_T2]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Turn [collections.abc.Sequence][]-returning function into a function
    expecting and returning [trcks.AwaitableSequence][]s
    of varying length.

    Args:
        f:
            The [collections.abc.Sequence][]-returning function to be transformed
            into a function expecting and returning
            [trcks.AwaitableSequence][]s of varying length.

    Returns:
        The given function transformed into
            a function expecting and returning
            [trcks.AwaitableSequence][]s of varying length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.map_to_sequence(lambda n: [n, -n]),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [1, -1, 2, -2]
    """
    return a.map_(s.map_to_sequence(f))


def tap(
    f: Callable[[_T1], object],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Turn synchronous function into a function
    expecting a [trcks.AwaitableSequence][] and
    returning the same [trcks.AwaitableSequence][].

    Args:
        f:
            The synchronous function to be transformed into a function
            expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> def log_integer(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap(log_integer),
        ...         )
        ...     )
        >>> seq = asyncio.run(main())
        Received: 1
        Received: 2
        >>> seq
        [1, 2]
    """
    return a.map_(s.tap(f))


def tap_to_awaitable(
    f: Callable[[_T1], Awaitable[object]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Turn [collections.abc.Awaitable][]-returning function into a function
    expecting a [trcks.AwaitableSequence][] and
    returning the same [trcks.AwaitableSequence][].

    Args:
        f:
            The [collections.abc.Awaitable][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def log_integer(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Received: {n}")
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap_to_awaitable(log_integer),
        ...         )
        ...     )
        >>> seq = asyncio.run(main())
        Received: 1
        Received: 2
        >>> seq
        [1, 2]
    """

    async def bypassed_f(t1: _T1) -> _T1:
        _ = await f(t1)
        return t1

    return map_to_awaitable(bypassed_f)


def tap_to_awaitable_sequence(
    f: Callable[[_T1], AwaitableSequence[object]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Turn [trcks.AwaitableSequence][]-returning function into a function
    expecting a [trcks.AwaitableSequence][] and
    returning the same [trcks.AwaitableSequence][].

    Args:
        f:
            The [trcks.AwaitableSequence][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def echo_twice(n: int) -> list[str]:
        ...     await asyncio.sleep(0.001)
        ...     return [str(n), str(n)]
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap_to_awaitable_sequence(echo_twice),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [1, 1, 2, 2]
    """

    async def bypassed_f(t1: _T1) -> Sequence[_T1]:
        objs = await f(t1)
        return [t1 for _ in objs]

    return map_to_awaitable_sequence(bypassed_f)


def tap_to_sequence(
    f: Callable[[_T1], Sequence[object]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Turn [collections.abc.Sequence][]-returning function into a function
    expecting a [trcks.AwaitableSequence][] and
    returning the same [trcks.AwaitableSequence][].

    Args:
        f:
            The [collections.abc.Sequence][]-returning function to be transformed
            into a function expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Returns:
        The given function transformed into a function
            expecting a [trcks.AwaitableSequence][] and
            returning the same [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap_to_sequence(lambda n: (n, n)),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [1, 1, 2, 2]
    """
    return a.map_(s.tap_to_sequence(f))


async def to_coroutine_sequence(a_seq: AwaitableSequence[_T]) -> Sequence[_T]:
    """Turn a [trcks.AwaitableSequence][] into a coroutine.

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        a_seq: The [trcks.AwaitableSequence][] to be transformed
            into a coroutine.

    Returns:
        The given [trcks.AwaitableSequence][] transformed
            into a coroutine.

    Note:
        The type [trcks.AwaitableSequence][] is
        an alias of [collections.abc.Awaitable][] over
        [collections.abc.Sequence][] values.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableSequence
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> a_seq: AwaitableSequence[int] = as_.construct_from_sequence([3, 4])
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [3, 4]
    """
    return await a_seq
