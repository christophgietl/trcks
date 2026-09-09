"""Monadic functions for [trcks.ResultTuple][].

Provides utilities for functional composition of
functions returning [trcks.ResultTuple][] values.

Examples:
    Map and tap each element inside a success tuple:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result_tuple as rt
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> result_tuple = pipe(
    ...     (
    ...         rt.construct_successes_from_iterable((1, 2, 3)),
    ...         rt.map_successes(double_integer),
    ...         rt.tap_successes(log_integer),
    ...         rt.map_successes_to_iterable(duplicate_integer),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> result_tuple
    ('success', (2, 2, 4, 4, 6, 6))
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import TypeVar
from trcks.fp._monads import awaitable_result_tuple as art
from trcks.fp._monads.result_tuple import (
    construct_failure,
    construct_from_result,
    construct_from_result_iterable,
    construct_successes,
    construct_successes_from_iterable,
    construct_successes_from_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_failure,
    map_failure_to_iterable,
    map_failure_to_result,
    map_failure_to_result_iterable,
    map_failure_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_failure_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_successes,
    map_successes_to_iterable,
    map_successes_to_result,
    map_successes_to_result_iterable,
    map_successes_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    map_successes_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_failure,
    tap_failure_to_iterable,
    tap_failure_to_result,
    tap_failure_to_result_iterable,
    tap_failure_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_failure_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_successes,
    tap_successes_to_iterable,
    tap_successes_to_result,
    tap_successes_to_result_iterable,
    tap_successes_to_result_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
    tap_successes_to_tuple,  # pyright: ignore[reportDeprecated]  # pyrefly: ignore[deprecated]
)
from trcks.fp.composition import compose2

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from trcks import (
        AwaitableIterable,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        ResultTuple,
        SuccessTuple,
    )

__all__ = [
    "construct_failure",
    "construct_from_result",
    "construct_from_result_iterable",
    "construct_successes",
    "construct_successes_from_iterable",
    "construct_successes_from_tuple",
    "map_failure",
    "map_failure_to_awaitable",
    "map_failure_to_awaitable_iterable",
    "map_failure_to_awaitable_result",
    "map_failure_to_awaitable_result_iterable",
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
    "tap_successes_to_iterable",
    "tap_successes_to_result",
    "tap_successes_to_result_iterable",
    "tap_successes_to_result_tuple",
    "tap_successes_to_tuple",
]
__docformat__ = "google"

_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_P = ParamSpec("_P")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def map_failure_to_awaitable(
    f: Callable[Concatenate[_F1, _P], Awaitable[_F2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.AwaitableFailure][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to [trcks.AwaitableFailure][] values
            according to the given asynchronous function and
            leaves [trcks.Success][] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def prefix_slowly(e: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"err: {e}"
        ...
        >>> add_prefix_to_failure = rt.map_failure_to_awaitable(prefix_slowly)
        >>> a_r_tpl_1 = add_prefix_to_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'err: not found')
        >>> a_r_tpl_2 = add_prefix_to_failure(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_failure_to_awaitable(f, *args, **kwargs),
        )
    )


def map_failure_to_awaitable_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableIterable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [ResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Create function that maps [trcks.Failure][] values
    to new [trcks.AwaitableSuccessTuple][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Failure][] values,
            returning an [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.AwaitableSuccessTuple][]
            values according to the given asynchronous function and
            leaves [trcks.Success][] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_recover_from_failure(description: str) -> list[int]:
        ...     await asyncio.sleep(0.001)
        ...     if description == "not found":
        ...         return [0]
        ...     return []
        ...
        >>> recover_from_failure = rt.map_failure_to_awaitable_iterable(
        ...     slowly_recover_from_failure
        ... )
        >>> a_r_tpl_1 = recover_from_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_failure(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    c: tuple[
        Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]],
        Callable[
            [AwaitableResultTuple[_F1, _S1]],
            Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
        ],
    ] = (
        art.construct_from_result_iterable,
        art.map_failure_to_awaitable_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def map_failure_to_awaitable_result(
    f: Callable[Concatenate[_F1, _P], AwaitableResult[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.AwaitableResult][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values
            to [trcks.AwaitableFailure][] and [trcks.AwaitableSuccess][] values
            according to the given asynchronous function and
            leaves [trcks.Success][] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_recover_from_not_found(e: str) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", 0
        ...     return "failure", e
        ...
        >>> recover_from_failure = rt.map_failure_to_awaitable_result(
        ...     slowly_recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_failure(("failure", "fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_failure(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_failure_to_awaitable_result(f, *args, **kwargs),
        )
    )


def map_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.AwaitableResultTuple][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.AwaitableResultTuple][] values
            according to the given asynchronous function and
            leaves [trcks.Success][] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def recover(e: str) -> AwaitableResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0, 1)
        ...     return "failure", e
        ...
        >>> recover_from_failure = rt.map_failure_to_awaitable_result_iterable(
        ...     recover
        ... )
        >>> a_r_tpl_1 = recover_from_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0, 1))
        >>> a_r_tpl_2 = recover_from_failure(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_failure_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def map_successes_to_awaitable(
    f: Callable[Concatenate[_S1, _P], Awaitable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.AwaitableSuccess][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to new [trcks.AwaitableSuccess][]
            values according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def double_slowly(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n * 2
        ...
        >>> double_successes = rt.map_successes_to_awaitable(double_slowly)
        >>> a_r_tpl_1 = double_successes(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = double_successes(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (2, 4))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_successes_to_awaitable(f, *args, **kwargs),
        )
    )


def map_successes_to_awaitable_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableIterable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values to homogeneous [tuple][]s
    and flattens the result.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to each success element,
            returning an [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to flattened
            [trcks.AwaitableSuccessTuple][] values
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_duplicate_integer(n: int) -> tuple[int, int]:
        ...     await asyncio.sleep(0.001)
        ...     return n, n
        ...
        >>> duplicate_successes = rt.map_successes_to_awaitable_iterable(
        ...     slowly_duplicate_integer
        ... )
        >>> a_r_tpl_1 = duplicate_successes(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = duplicate_successes(("failure", "oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_successes_to_awaitable_iterable(f, *args, **kwargs),
        )
    )


def map_successes_to_awaitable_result(
    f: Callable[Concatenate[_S1, _P], AwaitableResult[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.AwaitableResult][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values
            to [trcks.AwaitableFailure][] and [trcks.AwaitableSuccess][] values
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_double_if_positive(n: int) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", n * 2
        ...     return "failure", "negative"
        ...
        >>> double_successes = rt.map_successes_to_awaitable_result(
        ...     slowly_double_if_positive
        ... )
        >>> a_r_tpl_1 = double_successes(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = double_successes(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (2, 4))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_successes_to_awaitable_result(f, *args, **kwargs),
        )
    )


def map_successes_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.AwaitableResultTuple][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to new [trcks.AwaitableResultTuple][]
            values according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_expand(n: int) -> AwaitableResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", (n, -n)
        ...     return "failure", "negative"
        ...
        >>> expand_successes = rt.map_successes_to_awaitable_result_iterable(
        ...     slowly_expand
        ... )
        >>> a_r_tpl_1 = expand_successes(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = expand_successes(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, -1, 2, -2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.map_successes_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable(
    f: Callable[Concatenate[_F1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Failure][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and
            returns the original [trcks.Failure][] value.
            Passes on [trcks.Success][] values without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def log_slowly(e: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Error: {e}")
        ...
        >>> log_failure = rt.tap_failure_to_awaitable(log_slowly)
        >>> a_r_tpl_1 = log_failure(("failure", "oops"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Error: oops
        >>> r_tpl_1
        ('failure', 'oops')
        >>> a_r_tpl_2 = log_failure(("success", (1,)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1,))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_failure_to_awaitable(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableIterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [ResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableIterable][] to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Failure][] value,
            returning an [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and
            converts them to [trcks.AwaitableSuccessTuple][] values containing
            the original failure repeated once per element
            in the [trcks.AwaitableIterable][] returned by the side effect.
            Passes on [trcks.Success][] values without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_log_and_alert(description: str) -> tuple[None, None]:
        ...     await asyncio.sleep(0.001)
        ...     return (
        ...         print(f"Failure: {description}"),
        ...         print(f"Logged: {description}"),
        ...     )
        ...
        >>> log_and_alert = rt.tap_failure_to_awaitable_iterable(
        ...     slowly_log_and_alert
        ... )
        >>> a_r_tpl_1 = log_and_alert(("failure", "critical"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: critical
        Logged: critical
        >>> r_tpl_1
        ('success', ('critical', 'critical'))
        >>> a_r_tpl_2 = log_and_alert(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    c: tuple[
        Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]],
        Callable[
            [AwaitableResultTuple[_F1, _S1]],
            Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
        ],
    ] = (
        art.construct_from_result_iterable,
        art.tap_failure_to_awaitable_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def tap_failure_to_awaitable_result(
    f: Callable[Concatenate[_F1, _P], AwaitableResult[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1 | _S2]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][] to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Failure][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned (wrapped as a tuple).
            Passes on [trcks.Success][] values without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def recover(e: str) -> Result[object, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", 0
        ...     return "failure", e
        ...
        >>> recover_after_failure = rt.tap_failure_to_awaitable_result(recover)
        >>> a_r_tpl_1 = recover_after_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_after_failure(("success", (1,)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1,))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_failure_to_awaitable_result(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableResultIterable[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1 | _S2]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResultIterable][] to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Failure][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *this* [trcks.SuccessIterable][] is returned.
            Passes on [trcks.Success][] values without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def recover(e: str) -> AwaitableResultTuple[object, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0, 1)
        ...     return "failure", e
        ...
        >>> recover_after_failure = rt.tap_failure_to_awaitable_result_iterable(
        ...     recover
        ... )
        >>> a_r_tpl_1 = recover_after_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0, 1))
        >>> a_r_tpl_2 = recover_after_failure(("success", (1,)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1,))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_failure_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def tap_successes_to_awaitable(
    f: Callable[Concatenate[_S1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values and
            returns the original [trcks.Success][] value.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def print_slowly(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Value: {n}")
        ...
        >>> print_successes = rt.tap_successes_to_awaitable(print_slowly)
        >>> a_r_tpl_1 = print_successes(("failure", "oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'oops')
        >>> a_r_tpl_2 = print_successes(("success", (1, 2)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        Value: 1
        Value: 2
        >>> r_tpl_2
        ('success', (1, 2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_successes_to_awaitable(f, *args, **kwargs),
        )
    )


def tap_successes_to_awaitable_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableIterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableIterable][] to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element,
            returning an [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values and
            repeats each original element once per element
            in the [trcks.AwaitableIterable][] returned by the side effect.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_log_twice(n: int) -> tuple[None, None]:
        ...     await asyncio.sleep(0.001)
        ...     return print(f"Received: {n}"), print(f"Received: {n}")
        ...
        >>> log_successes = rt.tap_successes_to_awaitable_iterable(slowly_log_twice)
        >>> a_r_tpl = log_successes(("success", (7,)))
        >>> r_tpl = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Received: 7
        Received: 7
        >>> r_tpl
        ('success', (7, 7))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_successes_to_awaitable_iterable(f, *args, **kwargs),
        )
    )


def tap_successes_to_awaitable_result(
    f: Callable[Concatenate[_S1, _P], AwaitableResult[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][] to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.Success][] value is returned.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def slowly_check_if_positive(n: int) -> Result[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", None
        ...     return "failure", "negative"
        ...
        >>> check_successes = rt.tap_successes_to_awaitable_result(
        ...     slowly_check_if_positive
        ... )
        >>> a_r_tpl_1 = check_successes(("failure", "oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'oops')
        >>> a_r_tpl_2 = check_successes(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_successes_to_awaitable_result(f, *args, **kwargs),
        )
    )


def tap_successes_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[ResultTuple[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResultIterable][] to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* [trcks.Success][] value is repeated once per element
            in the returned [trcks.SuccessIterable][].

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result_tuple as rt
        >>> async def audit(n: int) -> AwaitableResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "negative"
        ...
        >>> audit_successes = rt.tap_successes_to_awaitable_result_iterable(audit)
        >>> a_r_tpl_1 = audit_successes(("failure", "oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'oops')
        >>> a_r_tpl_2 = audit_successes(("success", (1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 1, 2, 2))
    """
    return compose2(
        (
            art.construct_from_result_iterable,
            art.tap_successes_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )
