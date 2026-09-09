"""Monadic functions for [trcks.AwaitableResultTuple][].

Provides utilities for functional composition of
asynchronous [trcks.ResultTuple][]-returning functions.

Examples:
    Map and tap each element inside an awaitable success tuple:

    >>> import asyncio
    >>> from trcks import Result
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_result_tuple as art
    >>> async def slowly_read_from_disk() -> Result[str, int]:
    ...     await asyncio.sleep(0.001)
    ...     return "success", 3
    ...
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> async def main() -> Result[str, tuple[int, ...]]:
    ...     return await pipe(
    ...         (
    ...             art.construct_from_awaitable_result(slowly_read_from_disk()),
    ...             art.map_successes(double_integer),
    ...             art.tap_successes(log_integer),
    ...             art.map_successes_to_iterable(duplicate_integer),
    ...         )
    ...     )
    ...
    >>> r_tpl = asyncio.run(main())
    Received: 6
    >>> r_tpl
    ('success', (6, 6))
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import TypeVar, deprecated
from trcks.fp._monads.awaitable_result_tuple import (
    construct_failure,
    construct_failure_from_awaitable,
    construct_from_awaitable_result,
    construct_from_awaitable_result_iterable,
    construct_from_result,
    construct_from_result_iterable,
    construct_successes,
    construct_successes_from_awaitable,
    construct_successes_from_awaitable_iterable,
    construct_successes_from_iterable,
    map_failure,
    map_failure_to_awaitable,
    map_failure_to_awaitable_iterable,
    map_failure_to_awaitable_result,
    map_failure_to_awaitable_result_iterable,
    map_failure_to_iterable,
    map_failure_to_result,
    map_failure_to_result_iterable,
    map_successes,
    map_successes_to_awaitable,
    map_successes_to_awaitable_iterable,
    map_successes_to_awaitable_result,
    map_successes_to_awaitable_result_iterable,
    map_successes_to_iterable,
    map_successes_to_result,
    map_successes_to_result_iterable,
    tap_failure,
    tap_failure_to_awaitable,
    tap_failure_to_awaitable_iterable,
    tap_failure_to_awaitable_result,
    tap_failure_to_awaitable_result_iterable,
    tap_failure_to_iterable,
    tap_failure_to_result,
    tap_failure_to_result_iterable,
    tap_successes,
    tap_successes_to_awaitable,
    tap_successes_to_awaitable_iterable,
    tap_successes_to_awaitable_result,
    tap_successes_to_awaitable_result_iterable,
    tap_successes_to_iterable,
    tap_successes_to_result,
    tap_successes_to_result_iterable,
    to_coroutine_result_tuple,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from trcks import (
        AwaitableResultTuple,
        AwaitableSuccessTuple,
        AwaitableTuple,
        ResultTuple,
        SuccessTuple,
    )

__all__ = [
    "construct_failure",
    "construct_failure_from_awaitable",
    "construct_from_awaitable_result",
    "construct_from_awaitable_result_iterable",
    "construct_from_result",
    "construct_from_result_iterable",
    "construct_from_result_tuple",
    "construct_successes",
    "construct_successes_from_awaitable",
    "construct_successes_from_awaitable_iterable",
    "construct_successes_from_iterable",
    "construct_successes_from_tuple",
    "map_failure",
    "map_failure_to_awaitable",
    "map_failure_to_awaitable_iterable",
    "map_failure_to_awaitable_result",
    "map_failure_to_awaitable_result_iterable",
    "map_failure_to_awaitable_result_tuple",
    "map_failure_to_awaitable_tuple",
    "map_failure_to_iterable",
    "map_failure_to_result",
    "map_failure_to_result_iterable",
    "map_failure_to_result_tuple",
    "map_failure_to_tuple",
    "map_successes",
    "map_successes_to_awaitable",
    "map_successes_to_awaitable_iterable",
    "map_successes_to_awaitable_result",
    "map_successes_to_awaitable_result_iterable",
    "map_successes_to_awaitable_result_tuple",
    "map_successes_to_awaitable_tuple",
    "map_successes_to_iterable",
    "map_successes_to_result",
    "map_successes_to_result_iterable",
    "map_successes_to_result_tuple",
    "map_successes_to_tuple",
    "tap_failure",
    "tap_failure_to_awaitable",
    "tap_failure_to_awaitable_iterable",
    "tap_failure_to_awaitable_result",
    "tap_failure_to_awaitable_result_iterable",
    "tap_failure_to_awaitable_result_tuple",
    "tap_failure_to_awaitable_tuple",
    "tap_failure_to_iterable",
    "tap_failure_to_result",
    "tap_failure_to_result_iterable",
    "tap_failure_to_result_tuple",
    "tap_failure_to_tuple",
    "tap_successes",
    "tap_successes_to_awaitable",
    "tap_successes_to_awaitable_iterable",
    "tap_successes_to_awaitable_result",
    "tap_successes_to_awaitable_result_iterable",
    "tap_successes_to_awaitable_result_tuple",
    "tap_successes_to_awaitable_tuple",
    "tap_successes_to_iterable",
    "tap_successes_to_result",
    "tap_successes_to_result_iterable",
    "tap_successes_to_result_tuple",
    "tap_successes_to_tuple",
    "to_coroutine_result_tuple",
]
__docformat__ = "google"

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


@deprecated("Use construct_from_result_iterable instead")
def construct_from_result_tuple(
    r_tpl: ResultTuple[_F, _S],
) -> AwaitableResultTuple[_F, _S]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.construct_from_result_iterable][].
    """
    return construct_from_result_iterable(r_tpl)  # pragma: no cover


@deprecated("Use construct_successes_from_iterable instead")
def construct_successes_from_tuple(
    tpl: tuple[_S, ...],
) -> AwaitableSuccessTuple[_S]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.construct_successes_from_iterable][].
    """
    return construct_successes_from_iterable(tpl)  # pragma: no cover


@deprecated("Use map_failure_to_awaitable_result_iterable instead")
def map_failure_to_awaitable_result_tuple(
    f: Callable[Concatenate[_F1, _P], AwaitableResultTuple[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_awaitable_result_iterable][].
    """
    return map_failure_to_awaitable_result_iterable(
        f, *args, **kwargs
    )  # pragma: no cover


@deprecated("Use map_failure_to_awaitable_iterable instead")
def map_failure_to_awaitable_tuple(
    f: Callable[Concatenate[_F1, _P], AwaitableTuple[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_awaitable_iterable][].
    """
    return map_failure_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_failure_to_result_iterable instead")
def map_failure_to_result_tuple(
    f: Callable[Concatenate[_F1, _P], ResultTuple[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_result_iterable][].
    """
    return map_failure_to_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_failure_to_iterable instead")
def map_failure_to_tuple(
    f: Callable[Concatenate[_F1, _P], tuple[_S2, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_iterable][].
    """
    return map_failure_to_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_successes_to_awaitable_result_iterable instead")
def map_successes_to_awaitable_result_tuple(
    f: Callable[Concatenate[_S1, _P], AwaitableResultTuple[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_awaitable_result_iterable][].
    """
    return map_successes_to_awaitable_result_iterable(
        f, *args, **kwargs
    )  # pragma: no cover


@deprecated("Use map_successes_to_awaitable_iterable instead")
def map_successes_to_awaitable_tuple(
    f: Callable[Concatenate[_S1, _P], AwaitableTuple[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_awaitable_iterable][].
    """
    return map_successes_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_successes_to_result_iterable instead")
def map_successes_to_result_tuple(
    f: Callable[Concatenate[_S1, _P], ResultTuple[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_result_iterable][].
    """
    return map_successes_to_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_successes_to_iterable instead")
def map_successes_to_tuple(
    f: Callable[Concatenate[_S1, _P], tuple[_S2, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_iterable][].
    """
    return map_successes_to_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_failure_to_awaitable_result_iterable instead")
def tap_failure_to_awaitable_result_tuple(
    f: Callable[Concatenate[_F1, _P], AwaitableResultTuple[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_awaitable_result_iterable][].
    """
    return tap_failure_to_awaitable_result_iterable(
        f, *args, **kwargs
    )  # pragma: no cover


@deprecated("Use tap_failure_to_awaitable_iterable instead")
def tap_failure_to_awaitable_tuple(
    f: Callable[Concatenate[_F1, _P], AwaitableTuple[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_awaitable_iterable][].
    """
    return tap_failure_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_failure_to_result_iterable instead")
def tap_failure_to_result_tuple(
    f: Callable[Concatenate[_F1, _P], ResultTuple[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_result_iterable][].
    """
    return tap_failure_to_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_failure_to_iterable instead")
def tap_failure_to_tuple(
    f: Callable[Concatenate[_F1, _P], tuple[object, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_iterable][].
    """
    return tap_failure_to_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_successes_to_awaitable_result_iterable instead")
def tap_successes_to_awaitable_result_tuple(
    f: Callable[Concatenate[_S1, _P], AwaitableResultTuple[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_awaitable_result_iterable][].
    """
    return tap_successes_to_awaitable_result_iterable(
        f, *args, **kwargs
    )  # pragma: no cover


@deprecated("Use tap_successes_to_awaitable_iterable instead")
def tap_successes_to_awaitable_tuple(
    f: Callable[Concatenate[_S1, _P], AwaitableTuple[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_awaitable_iterable][].
    """
    return tap_successes_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_successes_to_result_iterable instead")
def tap_successes_to_result_tuple(
    f: Callable[Concatenate[_S1, _P], ResultTuple[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_result_iterable][].
    """
    return tap_successes_to_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_successes_to_iterable instead")
def tap_successes_to_tuple(
    f: Callable[Concatenate[_S1, _P], tuple[object, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_iterable][].
    """
    return tap_successes_to_iterable(f, *args, **kwargs)  # pragma: no cover
