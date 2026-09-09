"""Monadic functions for [trcks.AwaitableTuple][].

Provides utilities for functional composition of
asynchronous homogeneous-[tuple][]-returning functions.

Examples:
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

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import TypeVar, deprecated
from trcks.fp._monads.awaitable_tuple import (
    construct,
    construct_from_awaitable,
    construct_from_awaitable_iterable,
    construct_from_iterable,
    map_,
    map_to_awaitable,
    map_to_awaitable_iterable,
    map_to_iterable,
    tap,
    tap_to_awaitable,
    tap_to_awaitable_iterable,
    tap_to_iterable,
    to_coroutine_tuple,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks import AwaitableTuple

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

_P = ParamSpec("_P")
_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


@deprecated("Use construct_from_iterable instead")
def construct_from_tuple(tpl: tuple[_T, ...]) -> AwaitableTuple[_T]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.construct_from_iterable][].
    """
    return construct_from_iterable(tpl)  # pragma: no cover


@deprecated("Use map_to_awaitable_iterable instead")
def map_to_awaitable_tuple(
    f: Callable[Concatenate[_T1, _P], AwaitableTuple[_T2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.map_to_awaitable_iterable][].
    """
    return map_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_to_iterable instead")
def map_to_tuple(
    f: Callable[Concatenate[_T1, _P], tuple[_T2, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Deprecated alias for [trcks.fp.monads.awaitable_tuple.map_to_iterable][]."""
    return map_to_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_to_awaitable_iterable instead")
def tap_to_awaitable_tuple(
    f: Callable[Concatenate[_T1, _P], AwaitableTuple[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.tap_to_awaitable_iterable][].
    """
    return tap_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_to_iterable instead")
def tap_to_tuple(
    f: Callable[Concatenate[_T1, _P], tuple[object, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Deprecated alias for [trcks.fp.monads.awaitable_tuple.tap_to_iterable][]."""
    return tap_to_iterable(f, *args, **kwargs)  # pragma: no cover
