"""Monadic functions for [trcks.AwaitableSequence][].

Provides utilities for functional composition of
asynchronous [collections.abc.Sequence][]-returning functions.

Example:
    Map and tap over an awaitable sequence:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_sequence as as_
    >>> def double(x: int) -> int:
    ...     return x * 2
    ...
    >>> async def main() -> Sequence[int]:
    ...     return await pipe(
    ...         (
    ...             as_.construct_from_sequence((4, 2, 0)),
    ...             as_.map_(double),
    ...             as_.tap(lambda x: print(f"Processed: {x}")),
    ...         )
    ...     )
    ...
    >>> result = asyncio.run(main())
    Processed: 8
    Processed: 4
    Processed: 0
    >>> result
    [8, 4, 0]

    Map each element to an awaitable sequence and flatten the result:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_sequence as as_
    >>> async def duplicate(x: int) -> list[int]:
    ...     await asyncio.sleep(0.001)
    ...     return [x, x]
    ...
    >>> async def main() -> Sequence[int]:
    ...     return await pipe(
    ...         (
    ...             as_.construct_from_sequence((1, 2, 3)),
    ...             as_.map_to_awaitable_sequence(duplicate),
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
    """Create a [trcks.AwaitableSequence][] object from a single value.

    Args:
        value: A single value.

    Returns:
        A [trcks.AwaitableSequence][] instance containing the single value.

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
    """Create a [trcks.AwaitableSequence][] object from an awaitable value.

    Args:
        awtbl: Awaitable value to be wrapped in a [trcks.AwaitableSequence][].

    Returns:
        A [trcks.AwaitableSequence][] instance containing
        the value of the given awaitable.

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
    """Create a [trcks.AwaitableSequence][] object from a sequence.

    Args:
        seq: Sequence to be wrapped in a [trcks.AwaitableSequence][].

    Returns:
        A [trcks.AwaitableSequence][] instance containing the given sequence.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks import AwaitableSequence
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> seq: Sequence[int] = [1, 2]
        >>> a_seq: AwaitableSequence[int] = as_.construct_from_sequence(seq)
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [1, 2]
    """
    return a.construct(seq)


def map_(
    f: Callable[[_T1], _T2],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Turn synchronous function into function mapping
    [trcks.AwaitableSequence][]s to [trcks.AwaitableSequence][]s
    of the same length.

    Args:
        f: Synchronous function to apply to each element.

    Returns:
        The given synchronous function transformed into a function
            mapping [trcks.AwaitableSequence][]s to
            [trcks.AwaitableSequence][]s of the same length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence((1, 2, 3)),
        ...             as_.map_(lambda x: x * 2),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [2, 4, 6]
    """
    return a.map_(s.map_(f))


def map_to_awaitable(
    f: Callable[[_T1], Awaitable[_T2]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Turn [collections.abc.Awaitable][]-returning function into function
    mapping [trcks.AwaitableSequence][]s to [trcks.AwaitableSequence][]s.

    Args:
        f: Asynchronous function to apply to each element.

    Returns:
        The given [collections.abc.Awaitable][]-returning function transformed
            into a function mapping [trcks.AwaitableSequence][]s to
            [trcks.AwaitableSequence][]s.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def add_one(x: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return x + 1
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
    """Turn [trcks.AwaitableSequence][]-returning function into function
    mapping [trcks.AwaitableSequence][]s to [trcks.AwaitableSequence][]s
    of varying length.

    Args:
        f: Asynchronous function returning a [trcks.AwaitableSequence][] for
            each element.

    Returns:
        The given [trcks.AwaitableSequence][]-returning function transformed
            into a function mapping [trcks.AwaitableSequence][]s to
            [trcks.AwaitableSequence][]s of varying length.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def duplicate(x: int) -> list[int]:
        ...     await asyncio.sleep(0.001)
        ...     return [x, x]
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.map_to_awaitable_sequence(duplicate),
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
    """Turn [collections.abc.Sequence][]-returning function into function
    mapping [trcks.AwaitableSequence][]s to [trcks.AwaitableSequence][]s
    of varying length.

    Args:
        f: Synchronous function returning a [collections.abc.Sequence][]
            for each element.

    Returns:
        The given [collections.abc.Sequence][]-returning function transformed
            into a function mapping [trcks.AwaitableSequence][]s to
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
        ...             as_.map_to_sequence(lambda x: [x, -x]),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [1, -1, 2, -2]
    """
    return a.map_(s.map_to_sequence(f))


def tap(
    f: Callable[[_T1], object],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Turn synchronous function into function applying a side effect
    to each element of a [trcks.AwaitableSequence][].

    Args:
        f: Synchronous side-effect function to apply to each element.

    Returns:
        The given synchronous function transformed into a function
            applying a side effect to each element of a
            [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap(lambda x: print(f"seen {x}")),
        ...         )
        ...     )
        >>> seq = asyncio.run(main())
        seen 1
        seen 2
        >>> seq
        [1, 2]
    """
    return a.map_(s.tap(f))


def tap_to_awaitable(
    f: Callable[[_T1], Awaitable[object]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Turn [collections.abc.Awaitable][]-returning function into function
    applying an asynchronous side effect to each element of a
    [trcks.AwaitableSequence][].

    Args:
        f: Asynchronous side-effect function to apply to each element.

    Returns:
        The given [collections.abc.Awaitable][]-returning function transformed
            into a function applying an asynchronous side effect to each
            element of a [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def log_async(x: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"logged {x}")
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap_to_awaitable(log_async),
        ...         )
        ...     )
        >>> seq = asyncio.run(main())
        logged 1
        logged 2
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
    """Turn [trcks.AwaitableSequence][]-returning function into function
    applying an asynchronous side effect to each element of a
    [trcks.AwaitableSequence][].

    Args:
        f: Asynchronous side-effect producing a [trcks.AwaitableSequence][]
            for each element.

    Returns:
        The given [trcks.AwaitableSequence][]-returning function transformed
            into a function applying an asynchronous side effect to each
            element of a [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def echo_twice(x: int) -> list[str]:
        ...     await asyncio.sleep(0.001)
        ...     return [str(x), str(x)]
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
    """Turn [collections.abc.Sequence][]-returning function into function
    applying a side effect to each element of a [trcks.AwaitableSequence][].

    Args:
        f: Synchronous side-effect producing a [collections.abc.Sequence][]
            for each element.

    Returns:
        The given [collections.abc.Sequence][]-returning function transformed
            into a function applying a side effect to each element of a
            [trcks.AwaitableSequence][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.tap_to_sequence(lambda x: (x, x)),
        ...         )
        ...     )
        >>> asyncio.run(main())
        [1, 1, 2, 2]
    """
    return a.map_(s.tap_to_sequence(f))


async def to_coroutine_sequence(a_seq: AwaitableSequence[_T]) -> Sequence[_T]:
    """Turn a [trcks.AwaitableSequence][] into a coroutine.

    Useful for functions expecting a coroutine (e.g., [asyncio.run][]).

    Args:
        a_seq: The [trcks.AwaitableSequence][] to be transformed.

    Returns:
        The given [trcks.AwaitableSequence][] transformed into a coroutine.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableSequence
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> a_seq: AwaitableSequence[int] = as_.construct_from_sequence((3, 4))
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        (3, 4)
    """
    return await a_seq
