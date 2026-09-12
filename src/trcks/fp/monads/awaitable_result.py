"""Monadic functions for [trcks.AwaitableResult][].

Provides utilities for functional composition of
asynchronous [trcks.Result][]-returning functions.

Examples:
    >>> import asyncio
    >>> import math
    >>> from trcks import Result
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_result as ar
    >>> async def read_from_disk() -> Result[str, float]:
    ...     await asyncio.sleep(0.001)
    ...     return "failure", "not found"
    ...
    >>> def get_square_root(x: float) -> Result[str, float]:
    ...     if x < 0:
    ...         return "failure", "negative value"
    ...     return "success", math.sqrt(x)
    ...
    >>> async def write_to_disk(output: float) -> None:
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{output}' to disk.")
    ...
    >>> async def main() -> Result[str, float]:
    ...     a_rslt = read_from_disk()
    ...     return await pipe(
    ...         (
    ...             a_rslt,
    ...             ar.map_success_to_result(get_square_root),
    ...             ar.tap_success_to_awaitable(write_to_disk),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    ('failure', 'not found')
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import TypeVar
from trcks.fp._monads import awaitable_result_tuple as art
from trcks.fp._monads.awaitable_result import (
    construct_failure,
    construct_failure_from_awaitable,
    construct_from_result,
    construct_success,
    construct_success_from_awaitable,
    map_failure,
    map_failure_to_awaitable,
    map_failure_to_awaitable_result,
    map_failure_to_result,
    map_success,
    map_success_to_awaitable,
    map_success_to_awaitable_result,
    map_success_to_result,
    tap_failure,
    tap_failure_to_awaitable,
    tap_failure_to_awaitable_result,
    tap_failure_to_result,
    tap_success,
    tap_success_to_awaitable,
    tap_success_to_awaitable_result,
    tap_success_to_result,
    to_coroutine_result,
)
from trcks.fp.composition import compose2

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        ResultIterable,
        SuccessTuple,
    )

__all__ = [
    "construct_failure",
    "construct_failure_from_awaitable",
    "construct_from_result",
    "construct_success",
    "construct_success_from_awaitable",
    "map_failure",
    "map_failure_to_awaitable",
    "map_failure_to_awaitable_result",
    "map_failure_to_awaitable_result_iterable",
    "map_failure_to_iterable",
    "map_failure_to_result",
    "map_failure_to_result_iterable",
    "map_success",
    "map_success_to_awaitable",
    "map_success_to_awaitable_result",
    "map_success_to_awaitable_result_iterable",
    "map_success_to_iterable",
    "map_success_to_result",
    "map_success_to_result_iterable",
    "tap_failure",
    "tap_failure_to_awaitable",
    "tap_failure_to_awaitable_result",
    "tap_failure_to_awaitable_result_iterable",
    "tap_failure_to_iterable",
    "tap_failure_to_result",
    "tap_failure_to_result_iterable",
    "tap_success",
    "tap_success_to_awaitable",
    "tap_success_to_awaitable_result",
    "tap_success_to_awaitable_result_iterable",
    "tap_success_to_iterable",
    "tap_success_to_result",
    "tap_success_to_result_iterable",
    "to_coroutine_result",
]
__docformat__ = "google"

_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_P = ParamSpec("_P")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def map_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F2, _S1 | _S2]]:
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
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def recover(e: str) -> AwaitableResultTuple[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", e
        ...
        >>> recover_from_failure = ar.map_failure_to_awaitable_result_iterable(
        ...     recover
        ... )
        >>> a_r_tpl_1 = recover_from_failure(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_from_failure(ar.construct_success(25.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (25.0,))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.map_failure_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def map_failure_to_iterable(
    f: Callable[Concatenate[_F1, _P], Iterable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResult[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Create function that maps [trcks.Failure][] values to homogeneous [tuple][]s.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.Failure][] values,
            returning an [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to homogeneous [tuple][]s wrapped
            in [trcks.AwaitableSuccessTuple][] values
            according to the given function and
            leaves [trcks.Success][] values unchanged (wrapped as a tuple).

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def recover(e: str) -> tuple[float, ...]:
        ...     if e == "not found":
        ...         return (0.0, 1.0)
        ...     return ()
        ...
        >>> recover_from_failure = ar.map_failure_to_iterable(recover)
        >>> a_r_tpl_1 = recover_from_failure(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_from_failure(ar.construct_success(25.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (25.0,))
    """
    c: tuple[
        Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1, _S1]],
        Callable[
            [AwaitableResultTuple[_F1, _S1]],
            Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
        ],
    ] = (
        art.construct_from_awaitable_result,
        art.map_failure_to_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def map_failure_to_result_iterable(
    f: Callable[Concatenate[_F1, _P], ResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.Failure][] values
    to new [trcks.ResultTuple][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.ResultTuple][] values
            according to the given function and
            leaves [trcks.Success][] values unchanged (wrapped as a tuple).

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def recover(e: str) -> ResultTuple[str, float]:
        ...     if e == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", e
        ...
        >>> recover_from_failure = ar.map_failure_to_result_iterable(recover)
        >>> a_r_tpl_1 = recover_from_failure(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_from_failure(ar.construct_success(25.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (25.0,))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.map_failure_to_result_iterable(f, *args, **kwargs),
        )
    )


def map_success_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.AwaitableResultTuple][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Success][] values.
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
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def slowly_expand(x: float) -> AwaitableResultTuple[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative"
        ...     return "success", (x, x * 2)
        ...
        >>> expand_success = ar.map_success_to_awaitable_result_iterable(
        ...     slowly_expand
        ... )
        >>> a_r_tpl_1 = expand_success(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = expand_success(ar.construct_success(5.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (5.0, 10.0))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.map_successes_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def map_success_to_iterable(
    f: Callable[Concatenate[_S1, _P], Iterable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values to homogeneous [tuple][]s.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.Success][] values,
            returning an [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to homogeneous [tuple][]s
            according to the given function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def duplicate(x: float) -> tuple[float, ...]:
        ...     return (x, x)
        ...
        >>> duplicate_success = ar.map_success_to_iterable(duplicate)
        >>> a_r_tpl_1 = duplicate_success(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = duplicate_success(ar.construct_success(5.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (5.0, 5.0))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.map_successes_to_iterable(f, *args, **kwargs),
        )
    )


def map_success_to_result_iterable(
    f: Callable[Concatenate[_S1, _P], ResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to new [trcks.ResultTuple][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.Success][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to new [trcks.ResultTuple][] values
            according to the given function.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def expand(x: float) -> ResultTuple[str, float]:
        ...     if x < 0:
        ...         return "failure", "negative"
        ...     return "success", (x, x * 2)
        ...
        >>> expand_success = ar.map_success_to_result_iterable(expand)
        >>> a_r_tpl_1 = expand_success(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = expand_success(ar.construct_success(5.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (5.0, 10.0))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.map_successes_to_result_iterable(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableResultIterable[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1, _S1 | _S2]]:
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
            Passes on [trcks.Success][] values (wrapped as a tuple)
            without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def recover(e: str) -> AwaitableResultTuple[object, float]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", e
        ...
        >>> recover_after_failure = ar.tap_failure_to_awaitable_result_iterable(
        ...     recover
        ... )
        >>> a_r_tpl_1 = recover_after_failure(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_after_failure(ar.construct_success(42))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (42,))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.tap_failure_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def tap_failure_to_iterable(
    f: Callable[Concatenate[_F1, _P], Iterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResult[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Create function that applies a [collections.abc.Iterable][]-returning
    side effect to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value,
            returning an [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and converts them
            to [trcks.AwaitableSuccessTuple][] values containing
            the original failure repeated once per element
            in the [collections.abc.Iterable][] returned by the side effect.
            Passes on [trcks.Success][] values (wrapped as a tuple)
            without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def log_err(e: str) -> tuple[None, ...]:
        ...     print(f"Error logged: {e}")
        ...     print(f"Alert sent: {e}")
        ...     return (None, None)
        ...
        >>> log_failure = ar.tap_failure_to_iterable(log_err)
        >>> a_r_tpl_1 = log_failure(ar.construct_failure("critical"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Error logged: critical
        Alert sent: critical
        >>> r_tpl_1
        ('success', ('critical', 'critical'))
        >>> a_r_tpl_2 = log_failure(ar.construct_success(42))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (42,))
    """
    c: tuple[
        Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1, _S1]],
        Callable[
            [AwaitableResultTuple[_F1, _S1]],
            Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
        ],
    ] = (
        art.construct_from_awaitable_result,
        art.tap_failure_to_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def tap_failure_to_result_iterable(
    f: Callable[Concatenate[_F1, _P], ResultIterable[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1, _S1 | _S2]]:
    """Create function that applies a side effect with return type
    [trcks.ResultIterable][] to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.
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
            Passes on [trcks.Success][] values (wrapped as a tuple)
            without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def recover(e: str) -> ResultTuple[object, float]:
        ...     if e == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", e
        ...
        >>> recover_after_failure = ar.tap_failure_to_result_iterable(recover)
        >>> a_r_tpl_1 = recover_after_failure(ar.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_after_failure(ar.construct_success(42))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (42,))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.tap_failure_to_result_iterable(f, *args, **kwargs),
        )
    )


def tap_success_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResultIterable][] to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values (wrapped as a tuple)
            without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* [trcks.Success][] value is repeated once per element
            in the returned [trcks.SuccessIterable][].

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def write_twice(s: str) -> AwaitableResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' twice.")
        ...     return "success", (None, None)
        ...
        >>> write_success_twice = ar.tap_success_to_awaitable_result_iterable(
        ...     write_twice
        ... )
        >>> a_r_tpl_1 = write_success_twice(ar.construct_failure("missing text"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'missing text')
        >>> a_r_tpl_2 = write_success_twice(ar.construct_success("Hello, world!"))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        Wrote 'Hello, world!' twice.
        >>> r_tpl_2
        ('success', ('Hello, world!', 'Hello, world!'))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.tap_successes_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def tap_success_to_iterable(
    f: Callable[Concatenate[_S1, _P], Iterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Create function that applies a [collections.abc.Iterable][]-returning
    side effect to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Success][] value,
            returning an [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values (wrapped as a tuple)
            without side effects.
            Applies the given side effect to [trcks.Success][] values and
            repeats the original element once per element
            in the [collections.abc.Iterable][] returned by the side effect.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def log_mult(n: int) -> tuple[None, ...]:
        ...     print(f"v={n}")
        ...     print(f"v={n}")
        ...     return (None, None)
        ...
        >>> log_success = ar.tap_success_to_iterable(log_mult)
        >>> a_r_tpl_1 = log_success(ar.construct_failure("error"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'error')
        >>> a_r_tpl_2 = log_success(ar.construct_success(7))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        v=7
        v=7
        >>> r_tpl_2
        ('success', (7, 7))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.tap_successes_to_iterable(f, *args, **kwargs),
        )
    )


def tap_success_to_result_iterable(
    f: Callable[Concatenate[_S1, _P], ResultIterable[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type
    [trcks.ResultIterable][] to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values (wrapped as a tuple)
            without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* [trcks.Success][] value is repeated once per element
            in the returned [trcks.SuccessIterable][].

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def audit(s: str) -> ResultTuple[str, None]:
        ...     if s:
        ...         return "success", (None, None)
        ...     return "failure", "empty"
        ...
        >>> audit_success = ar.tap_success_to_result_iterable(audit)
        >>> a_r_tpl_1 = audit_success(ar.construct_failure("missing"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'missing')
        >>> a_r_tpl_2 = audit_success(ar.construct_success("Hello, world!"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', ('Hello, world!', 'Hello, world!'))
    """
    return compose2(
        (
            art.construct_from_awaitable_result,
            art.tap_successes_to_result_iterable(f, *args, **kwargs),
        )
    )
