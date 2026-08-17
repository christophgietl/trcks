"""Monadic functions for [trcks.Result][].

Provides utilities for functional composition of
synchronous [trcks.Result][]-returning functions.

Example:
    Create and process a value of type [trcks.Result][]:

    >>> import math
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result as r
    >>> rslt = pipe(
    ...     (
    ...         r.construct_success(1_000_000.0),
    ...         r.tap_success(lambda x: print(f"Processing value {x} ...")),
    ...         r.map_success_to_result(
    ...             lambda x: (
    ...                 ("success", math.sqrt(x))
    ...                 if x >= 0
    ...                 else ("failure", "negative value")
    ...             )
    ...         ),
    ...         r.tap_success_to_result(
    ...             lambda x: (
    ...                 ("success", print(f"Wrote result {x} to disk."))
    ...                 if x < 100
    ...                 else ("failure", "out of disk space")
    ...             )
    ...         ),
    ...     )
    ... )
    Processing value 1000000.0 ...
    >>> rslt
    ('failure', 'out of disk space')

    If your static type checker cannot infer the type of
    the argument passed to [trcks.fp.composition.pipe][],
    you can explicitly assign a type:

    >>> import math
    >>> from trcks import Result, Success
    >>> from trcks.fp.composition import Pipeline3, pipe
    >>> from trcks.fp.monads import result as r
    >>> p: Pipeline3[
    ...     Success[float],
    ...     Result[str, float],
    ...     Result[str, float],
    ...     Result[str, float],
    ... ] = (
    ...     r.construct_success(1_000_000.0),
    ...     r.tap_success(lambda x: print(f"Processing value {x} ...")),
    ...     r.map_success_to_result(
    ...         lambda x: (
    ...             ("success", math.sqrt(x))
    ...             if x >= 0
    ...             else ("failure", "negative value")
    ...         )
    ...     ),
    ...     r.tap_success_to_result(
    ...         lambda x: (
    ...             ("success", print(f"Wrote result {x} to disk."))
    ...             if x < 100
    ...             else ("failure", "out of disk space")
    ...         )
    ...     ),
    ... )
    >>> rslt = pipe(p)
    Processing value 1000000.0 ...
    >>> rslt
    ('failure', 'out of disk space')
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import TypeVar
from trcks.fp._monads import awaitable_result as ar
from trcks.fp._monads import awaitable_result_tuple as art
from trcks.fp._monads import result_tuple as rt
from trcks.fp._monads.result import (
    construct_failure,
    construct_success,
    map_failure,
    map_failure_to_result,
    map_success,
    map_success_to_result,
    tap_failure,
    tap_failure_to_result,
    tap_success,
    tap_success_to_result,
)
from trcks.fp.composition import compose2

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        Result,
        ResultIterable,
        ResultTuple,
        SuccessTuple,
    )

__all__ = [
    "construct_failure",
    "construct_success",
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
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F2, _S1]]:
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

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def add_prefix_slowly(s: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"Prefix: {s}"
        ...
        >>> add_prefix_to_failure = r.map_failure_to_awaitable(add_prefix_slowly)
        >>> a_rslt_1 = add_prefix_to_failure(("failure", "not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'Prefix: not found')
        >>> a_rslt_2 = add_prefix_to_failure(("success", 42))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 42)
    """
    return compose2(
        (ar.construct_from_result, ar.map_failure_to_awaitable(f, *args, **kwargs))
    )


def map_failure_to_awaitable_result(
    f: Callable[Concatenate[_F1, _P], AwaitableResult[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
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

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def slowly_replace_not_found(s: str) -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if s == "not found":
        ...         return "success", 0.0
        ...     return "failure", s
        ...
        >>> replace_not_found = r.map_failure_to_awaitable_result(
        ...     slowly_replace_not_found
        ... )
        >>> a_rslt_1 = replace_not_found(("failure", "not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('success', 0.0)
        >>> a_rslt_2 = replace_not_found(("failure", "other failure"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('failure', 'other failure')
        >>> a_rslt_3 = replace_not_found(("success", 25.0))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_3))
        ('success', 25.0)
    """
    return compose2(
        (
            ar.construct_from_result,
            ar.map_failure_to_awaitable_result(f, *args, **kwargs),
        )
    )


def map_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResultTuple[_F2, _S1 | _S2]]:
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

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result as r
        >>> async def recover(e: str) -> AwaitableResultTuple[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", e
        ...
        >>> recover_from_result = r.map_failure_to_awaitable_result_iterable(recover)
        >>> a_r_tpl_1 = recover_from_result(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_from_result(("success", 25.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (25.0,))
    """
    return compose2(
        (
            art.construct_from_result,
            art.map_failure_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def map_failure_to_iterable(
    f: Callable[Concatenate[_F1, _P], Iterable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], SuccessTuple[_S1] | SuccessTuple[_S2]]:
    """Create function that maps [trcks.Failure][] values to homogeneous [tuple][]s.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values,
            returning an [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to homogeneous [tuple][]s wrapped
            in a [trcks.Success][] according to the given function and
            leaves [trcks.Success][] values (wrapped as a tuple) unchanged.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> def recover(s: str) -> tuple[float, ...]:
        ...     if s == "not found":
        ...         return (0.0, 1.0)
        ...     return ()
        ...
        >>> recover_from_result = r.map_failure_to_iterable(recover)
        >>> recover_from_result(("failure", "not found"))
        ('success', (0.0, 1.0))
        >>> recover_from_result(("failure", "other error"))
        ('success', ())
        >>> recover_from_result(("success", 42))
        ('success', (42,))
    """
    mapped = rt.map_failure_to_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> SuccessTuple[_S1] | SuccessTuple[_S2]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def map_failure_to_result_iterable(
    f: Callable[Concatenate[_F1, _P], ResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], ResultTuple[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.Failure][] values
    to new [trcks.ResultTuple][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.ResultTuple][] values
            according to the given function and
            leaves [trcks.Success][] values (wrapped as a tuple) unchanged.

    Example:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result as r
        >>> def expand_error(s: str) -> ResultTuple[str, float]:
        ...     if s == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", s
        ...
        >>> expand_error_from_result = r.map_failure_to_result_iterable(expand_error)
        >>> expand_error_from_result(("failure", "not found"))
        ('success', (0.0, 1.0))
        >>> expand_error_from_result(("failure", "other error"))
        ('failure', 'other error')
        >>> expand_error_from_result(("success", 42))
        ('success', (42,))
    """
    mapped = rt.map_failure_to_result_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> ResultTuple[_F2, _S1 | _S2]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def map_success_to_awaitable(
    f: Callable[Concatenate[_S1, _P], Awaitable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.AwaitableSuccess][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Success][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to new [trcks.AwaitableSuccess][] values
            according to the given asynchronous function.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def increment_slowly(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n + 1
        ...
        >>> increase_success = r.map_success_to_awaitable(increment_slowly)
        >>> a_rslt_1 = increase_success(("failure", "not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not found')
        >>> a_rslt_2 = increase_success(("success", 42))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 43)
    """
    return compose2(
        (ar.construct_from_result, ar.map_success_to_awaitable(f, *args, **kwargs))
    )


def map_success_to_awaitable_result(
    f: Callable[Concatenate[_S1, _P], AwaitableResult[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.AwaitableResult][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Success][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values
            to [trcks.AwaitableFailure][] and [trcks.AwaitableSuccess][] values
            according to the given asynchronous function.

    Example:
        >>> import asyncio
        >>> import math
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def get_square_root_slowly(x: float) -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", math.sqrt(x)
        ...
        >>> get_square_root = r.map_success_to_awaitable_result(get_square_root_slowly)
        >>> a_rslt_1 = get_square_root(("failure", "not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not found')
        >>> a_rslt_2 = get_square_root(("success", -25.0))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('failure', 'negative value')
        >>> a_rslt_3 = get_square_root(("success", 25.0))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_3))
        ('success', 5.0)
    """
    return compose2(
        (
            ar.construct_from_result,
            ar.map_success_to_awaitable_result(f, *args, **kwargs),
        )
    )


def map_success_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S2]]:
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

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result as r
        >>> async def slowly_expand(x: float) -> AwaitableResultTuple[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative"
        ...     return "success", (x, x * 2)
        ...
        >>> expand_success = r.map_success_to_awaitable_result_iterable(slowly_expand)
        >>> a_r_tpl_1 = expand_success(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'not found')
        >>> a_r_tpl_2 = expand_success(("success", 5.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (5.0, 10.0))
    """
    return compose2(
        (
            art.construct_from_result,
            art.map_successes_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def map_success_to_iterable(
    f: Callable[Concatenate[_S1, _P], Iterable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], ResultTuple[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values to homogeneous [tuple][]s.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] values,
            returning an [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values (wrapped as a tuple) unchanged and
            maps [trcks.Success][] values to homogeneous [tuple][]s
            according to the given function.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> def duplicate(x: float) -> tuple[float, float]:
        ...     return (x, x)
        ...
        >>> duplicate_success = r.map_success_to_iterable(duplicate)
        >>> duplicate_success(("failure", "not found"))
        ('failure', 'not found')
        >>> duplicate_success(("success", 5.0))
        ('success', (5.0, 5.0))
    """
    mapped = rt.map_successes_to_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> ResultTuple[_F1, _S2]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def map_success_to_result_iterable(
    f: Callable[Concatenate[_S1, _P], ResultIterable[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], ResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to new [trcks.ResultTuple][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Leaves [trcks.Failure][] values (wrapped as a tuple) unchanged and
            maps [trcks.Success][] values to new [trcks.ResultTuple][] values
            according to the given function.

    Example:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result as r
        >>> def expand(x: float) -> ResultTuple[str, float]:
        ...     if x < 0:
        ...         return "failure", "negative"
        ...     return "success", (x, x * 2)
        ...
        >>> expand_success = r.map_success_to_result_iterable(expand)
        >>> expand_success(("failure", "not found"))
        ('failure', 'not found')
        >>> expand_success(("success", 5.0))
        ('success', (5.0, 10.0))
        >>> expand_success(("success", -5.0))
        ('failure', 'negative')
    """
    mapped = rt.map_successes_to_result_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> ResultTuple[_F1 | _F2, _S2]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def tap_failure_to_awaitable(
    f: Callable[Concatenate[_F1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F1, _S1]]:
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

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def write_to_disk(output: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{output}' to disk.")
        ...
        >>> write_failure_to_disk = r.tap_failure_to_awaitable(write_to_disk)
        >>> a_rslt_1 = write_failure_to_disk(("failure", "not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        Wrote 'not found' to disk.
        ('failure', 'not found')
        >>> a_rslt_2 = write_failure_to_disk(("success", 42))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 42)
    """
    return compose2(
        (ar.construct_from_result, ar.tap_failure_to_awaitable(f, *args, **kwargs))
    )


def tap_failure_to_awaitable_result(
    f: Callable[Concatenate[_F1, _P], AwaitableResult[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F1, _S1 | _S2]]:
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
            *this* [trcks.Success][] is returned.
            Passes on [trcks.Success][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def replace_not_found_with_default(
        ...     s: str,
        ... ) -> Result[object, float]:
        ...     await asyncio.sleep(0.001)
        ...     if s == "not found":
        ...         return "success", 0.0
        ...     return "failure", s
        ...
        >>> recover_from_failure = r.tap_failure_to_awaitable_result(
        ...     replace_not_found_with_default
        ... )
        >>> a_rslt_1 = recover_from_failure(("failure", "not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('success', 0.0)
        >>> a_rslt_2 = recover_from_failure(("failure", "other error"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('failure', 'other error')
        >>> a_rslt_3 = recover_from_failure(("success", 42))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_3))
        ('success', 42)
    """
    return compose2(
        (
            ar.construct_from_result,
            ar.tap_failure_to_awaitable_result(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], AwaitableResultIterable[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResultTuple[_F1, _S1 | _S2]]:
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

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result as r
        >>> async def recover(e: str) -> AwaitableResultTuple[object, float]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0.0, 1.0)
        ...     return "failure", e
        ...
        >>> recover_from_failure = r.tap_failure_to_awaitable_result_iterable(recover)
        >>> a_r_tpl_1 = recover_from_failure(("failure", "not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0.0, 1.0))
        >>> a_r_tpl_2 = recover_from_failure(("success", 42))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (42,))
    """
    return compose2(
        (
            art.construct_from_result,
            art.tap_failure_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def tap_failure_to_iterable(
    f: Callable[Concatenate[_F1, _P], Iterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], SuccessTuple[_F1] | SuccessTuple[_S1]]:
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
            to [trcks.SuccessTuple][] values containing the original failure
            repeated once per element in the [collections.abc.Iterable][] returned
            by the side effect.
            Passes on [trcks.Success][] values (wrapped as a tuple)
            without side effects.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> def log_err(e: str) -> tuple[None, ...]:
        ...     print(f"Error logged: {e}")
        ...     print(f"Alert sent: {e}")
        ...     return (None, None)
        ...
        >>> log_failure = r.tap_failure_to_iterable(log_err)
        >>> log_failure(("failure", "critical"))
        Error logged: critical
        Alert sent: critical
        ('success', ('critical', 'critical'))
        >>> log_failure(("success", 42))
        ('success', (42,))
    """
    mapped = rt.tap_failure_to_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> SuccessTuple[_F1] | SuccessTuple[_S1]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def tap_failure_to_result_iterable(
    f: Callable[Concatenate[_F1, _P], ResultIterable[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], ResultTuple[_F1, _S1 | _S2]]:
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

    Example:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result as r
        >>> def attempt_recover(s: str) -> ResultTuple[None, int]:
        ...     if s == "retry":
        ...         return "success", (99,)
        ...     return "failure", None
        ...
        >>> recover_failure = r.tap_failure_to_result_iterable(attempt_recover)
        >>> recover_failure(("failure", "retry"))
        ('success', (99,))
        >>> recover_failure(("failure", "fatal"))
        ('failure', 'fatal')
        >>> recover_failure(("success", 42))
        ('success', (42,))
    """
    mapped = rt.tap_failure_to_result_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> ResultTuple[_F1, _S1 | _S2]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def tap_success_to_awaitable(
    f: Callable[Concatenate[_S1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values and
            returns the original [trcks.Success][] value.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def write_to_disk(s: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' to disk.")
        ...
        >>> write_success_to_disk = r.tap_success_to_awaitable(write_to_disk)
        >>> a_rslt_1 = write_success_to_disk(("failure", "missing text"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'missing text')
        >>> a_rslt_2 = write_success_to_disk(("success", "Hello, world!"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        Wrote 'Hello, world!' to disk.
        ('success', 'Hello, world!')
    """
    return compose2(
        (ar.construct_from_result, ar.tap_success_to_awaitable(f, *args, **kwargs))
    )


def tap_success_to_awaitable_result(
    f: Callable[Concatenate[_S1, _P], AwaitableResult[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResult[_F1 | _F2, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][] to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.Success][] value.
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

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import result as r
        >>> async def write_to_disk(s: str, path: str) -> Result[str, None]:
        ...     if path != "output.txt":
        ...         return "failure", "write error"
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' to file {path}.")
        ...     return "success", None
        ...
        >>> write_success_to_output = r.tap_success_to_awaitable_result(
        ...     lambda s: write_to_disk(s, "output.txt")
        ... )
        >>> a_rslt_1 = write_success_to_output(("failure", "missing text"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'missing text')
        >>> a_rslt_2 = write_success_to_output(("success", "Hello, world!"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        Wrote 'Hello, world!' to file output.txt.
        ('success', 'Hello, world!')
    """
    return compose2(
        (
            ar.construct_from_result,
            ar.tap_success_to_awaitable_result(f, *args, **kwargs),
        )
    )


def tap_success_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], AwaitableResultTuple[_F1 | _F2, _S1]]:
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
        Passes on [trcks.Failure][] values (wrapped as a tuple) without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* [trcks.Success][] value is repeated once per element
            in the returned [trcks.SuccessIterable][].

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import result as r
        >>> async def write_twice(s: str) -> AwaitableResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' twice.")
        ...     return "success", (None, None)
        ...
        >>> write_success_twice = r.tap_success_to_awaitable_result_iterable(
        ...     write_twice
        ... )
        >>> a_r_tpl_1 = write_success_twice(("failure", "missing text"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'missing text')
        >>> a_r_tpl_2 = write_success_twice(("success", "Hello, world!"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        Wrote 'Hello, world!' twice.
        ('success', ('Hello, world!', 'Hello, world!'))
    """
    return compose2(
        (
            art.construct_from_result,
            art.tap_successes_to_awaitable_result_iterable(f, *args, **kwargs),
        )
    )


def tap_success_to_iterable(
    f: Callable[Concatenate[_S1, _P], Iterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], ResultTuple[_F1, _S1]]:
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
        Passes on [trcks.Failure][] values (wrapped as a tuple) without side effects.
            Applies the given side effect to [trcks.Success][] values and
            repeats the original element once per element in the
            [collections.abc.Iterable][] returned by the side effect.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> def log_mult(n: int) -> tuple[None, ...]:
        ...     print(f"v={n}")
        ...     print(f"v={n}")
        ...     return None, None
        ...
        >>> log_success = r.tap_success_to_iterable(log_mult)
        >>> log_success(("failure", "error"))
        ('failure', 'error')
        >>> log_success(("success", 7))
        v=7
        v=7
        ('success', (7, 7))
    """
    mapped = rt.tap_successes_to_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> ResultTuple[_F1, _S1]:
        return mapped(rt.construct_from_result(rslt))

    return widened


def tap_success_to_result_iterable(
    f: Callable[Concatenate[_S1, _P], ResultIterable[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], ResultTuple[_F1 | _F2, _S1]]:
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
        Passes on [trcks.Failure][] values (wrapped as a tuple) without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* [trcks.Success][] value is repeated once per element
            in the returned [trcks.SuccessIterable][].

    Example:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result as r
        >>> def audit(n: int) -> ResultTuple[str, None]:
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "negative"
        ...
        >>> audit_success = r.tap_success_to_result_iterable(audit)
        >>> audit_success(("failure", "oops"))
        ('failure', 'oops')
        >>> audit_success(("success", 7))
        ('success', (7, 7))
        >>> audit_success(("success", -1))
        ('failure', 'negative')
    """
    mapped = rt.tap_successes_to_result_iterable(f, *args, **kwargs)

    def widened(rslt: Result[_F1, _S1]) -> ResultTuple[_F1 | _F2, _S1]:
        return mapped(rt.construct_from_result(rslt))

    return widened
