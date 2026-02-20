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
    ...     a_seq = as_.construct(1)
    ...     return await pipe(
    ...         (
    ...             a_seq,
    ...             as_.map_(double),
    ...             as_.tap(lambda x: print(f"Processed: {x}")),
    ...         )
    ...     )
    ...
    >>> result = asyncio.run(main())
    Processed: 2
    >>> result
    [2]

    Map each element to an awaitable sequence and flatten the result:

    >>> import asyncio
    >>> from collections.abc import Sequence
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_sequence as as_
    >>> async def duplicate(x: int) -> list[int]:
    ...     await asyncio.sleep(0.001)
    ...     return [x, x]
    ...
    >>> async def main2() -> Sequence[int]:
    ...     a_seq = as_.construct_from_sequence((1, 2, 3))
    ...     return await pipe(
    ...         (
    ...             a_seq,
    ...             as_.map_to_awaitable_sequence(duplicate),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main2())
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
        A new [trcks.AwaitableSequence][] instance containing the single value.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> a_seq = as_.construct(42)
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [42]
    """
    return a.construct(s.construct(value))


def construct_from_awaitable(awtbl: Awaitable[_T]) -> AwaitableSequence[_T]:
    """Create a [trcks.AwaitableSequence][] object from an awaitable value.

    Args:
        awtbl: Awaitable value to be wrapped in a [trcks.AwaitableSequence][].

    Returns:
        A new [trcks.AwaitableSequence][] instance containing
        the value of the given awaitable.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def get_value() -> int:
        ...     return 7
        ...
        >>> a_seq = as_.construct_from_awaitable(get_value())
        >>> asyncio.run(as_.to_coroutine_sequence(a_seq))
        [7]
    """
    return a.map_(s.construct)(awtbl)


def construct_from_sequence(seq: Sequence[_T]) -> AwaitableSequence[_T]:
    """Create a [trcks.AwaitableSequence][] object from a sequence.

    Args:
        seq: Sequence to be wrapped in a [trcks.AwaitableSequence][].

    Returns:
        A new [trcks.AwaitableSequence][] instance containing the given sequence.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> asyncio.run(as_.to_coroutine_sequence(as_.construct_from_sequence([1, 2])))
        [1, 2]
    """
    return a.construct(seq)


def map_(
    f: Callable[[_T1], _T2],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T2]]:
    """Map a synchronous function over each element of a [trcks.AwaitableSequence][].

    Args:
        f: Function to apply to each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][] and yields a
        [trcks.AwaitableSequence][] with `f` applied element-wise.

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
    """Map an awaitable-returning function over a [trcks.AwaitableSequence][].

    Each element is transformed by the asynchronous function and the results
    are collected into a sequence.

    Args:
        f: Asynchronous function to apply to each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][] and returns a
        [trcks.AwaitableSequence][] of the transformed values.

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
    """Map a [trcks.AwaitableSequence][]-returning function and flatten results.

    Args:
        f: Asynchronous function returning a [trcks.AwaitableSequence][] for
            each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][], applies `f` to each
        element, awaits and flattens the resulting sequences.

    Example:
        >>> import asyncio
    >>> from collections.abc import Sequence
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> async def dup(x: int) -> list[int]:
        ...     await asyncio.sleep(0.001)
        ...     return [x, x]
        >>> async def main() -> Sequence[int]:
        ...     return await pipe(
        ...         (
        ...             as_.construct_from_sequence([1, 2]),
        ...             as_.map_to_awaitable_sequence(dup),
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
    """Map a sequence-returning function over a [trcks.AwaitableSequence][].

    Args:
        f: Function returning a sequence for each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][], applies `f` to each
        element, and returns a [trcks.AwaitableSequence][] of flattened values.

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
    """Apply a side effect to each element of a [trcks.AwaitableSequence][].

    Args:
        f: Side-effect function to apply to each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][], applies the side
        effect, and returns the original elements.

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
        >>> asyncio.run(main())
        seen 1
        seen 2
        [1, 2]
    """
    return a.map_(s.tap(f))


def tap_to_awaitable(
    f: Callable[[_T1], Awaitable[object]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Apply an awaitable side effect to each element of a [trcks.AwaitableSequence][].

    Args:
        f: Asynchronous side-effect function.

    Returns:
        Function that takes a [trcks.AwaitableSequence][], applies the side
        effect, and returns the original elements.

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
        >>> asyncio.run(main())
        logged 1
        logged 2
        [1, 2]
    """

    async def bypassed_f(t1: _T1) -> _T1:
        _ = await f(t1)
        return t1

    return map_to_awaitable(bypassed_f)


def tap_to_awaitable_sequence(
    f: Callable[[_T1], AwaitableSequence[object]],
) -> Callable[[AwaitableSequence[_T1]], AwaitableSequence[_T1]]:
    """Apply a [trcks.AwaitableSequence][]-returning side effect to each element.

    The number of side-effect outputs determines how many times each original
    element is repeated in the resulting sequence.

    Args:
        f: Asynchronous side-effect producing a sequence for each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][], applies the side
        effect, and returns a sequence of the original elements, replicated
        accordingly.

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
    """Apply a sequence-returning side effect to each element of a
    [trcks.AwaitableSequence][].

    The number of side-effect outputs determines how many times each original
    element is repeated in the resulting sequence.

    Args:
        f: Side-effect producing a sequence for each element.

    Returns:
        Function that takes a [trcks.AwaitableSequence][], applies the side
        effect, and returns a sequence of the original elements, replicated
        accordingly.

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
        >>> from trcks.fp.monads import awaitable_sequence as as_
        >>> coro = as_.to_coroutine_sequence(as_.construct_from_sequence((3, 4)))
        >>> asyncio.run(coro)
        (3, 4)
    """
    return await a_seq
