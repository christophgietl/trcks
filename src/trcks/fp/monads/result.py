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
    from collections.abc import Awaitable, Callable

    from trcks import (
        AwaitableResult,
        AwaitableResultTuple,
        Result,
        ResultTuple,
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

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")

__docformat__ = "google"

# Re-assign __module__ to match the facade module name for test compatibility
construct_failure.__module__ = __name__
construct_success.__module__ = __name__
map_failure.__module__ = __name__
map_failure_to_result.__module__ = __name__
map_success.__module__ = __name__
map_success_to_result.__module__ = __name__
tap_failure.__module__ = __name__
tap_failure_to_result.__module__ = __name__
tap_success.__module__ = __name__
tap_success_to_result.__module__ = __name__


# Widening functions - transition from Result to richer monad types


def map_failure_to_awaitable(
    f: Callable[Concatenate[_F1, _P], Awaitable[_F2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S]], AwaitableResult[_F2, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] mapping failures.

    Applies an asynchronous function to [trcks.Failure][] values.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Failure][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def add_prefix_slowly(s: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"Prefix: {s}"
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.map_failure_to_awaitable(add_prefix_slowly),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        ('failure', 'Prefix: error')
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (ar.construct_from_result, ar.map_failure_to_awaitable(f, *args, **kwargs))
    )


def map_failure_to_awaitable_result(
    f: Callable[Concatenate[_F1, _P], AwaitableResult[_F2, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S]], AwaitableResult[_F2, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] mapping failures.

    Applies an asynchronous function with return type [trcks.AwaitableResult][]
    to [trcks.Failure][] values. [trcks.Success][] values are passed on unchanged.

    Args:
        f: Asynchronous function returning [trcks.AwaitableResult][].
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def slowly_recover(err: str) -> tuple:
        ...     await asyncio.sleep(0.001)
        ...     return "success", f"Recovered from {err}"
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.map_failure_to_awaitable_result(slowly_recover),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        ('success', 'Recovered from error')
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (
            ar.construct_from_result,
            ar.map_failure_to_awaitable_result(f, *args, **kwargs),
        )
    )


def map_success_to_awaitable(
    f: Callable[Concatenate[_S1, _P], Awaitable[_S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S1]], AwaitableResult[_F, _S2]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] mapping successes.

    Applies an asynchronous function to [trcks.Success][] values.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Success][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def slowly_double(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n * 2
        ...
        >>> p = (
        ...     r.construct_success(21),
        ...     r.map_success_to_awaitable(slowly_double),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        ('success', 42)
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (ar.construct_from_result, ar.map_success_to_awaitable(f, *args, **kwargs))
    )


def map_success_to_awaitable_result(
    f: Callable[Concatenate[_S1, _P], AwaitableResult[_F, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S1]], AwaitableResult[_F, _S2]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] mapping successes.

    Applies an asynchronous function with return type [trcks.AwaitableResult][]
    to [trcks.Success][] values. [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Asynchronous function returning [trcks.AwaitableResult][].
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def slowly_get_square_root(n: float) -> tuple:
        ...     await asyncio.sleep(0.001)
        ...     if n < 0:
        ...         return "failure", "negative value"
        ...     return "success", n ** 0.5
        ...
        >>> p = (
        ...     r.construct_success(4.0),
        ...     r.map_success_to_awaitable_result(slowly_get_square_root),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        ('success', 2.0)
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (
            ar.construct_from_result,
            ar.map_success_to_awaitable_result(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable(
    f: Callable[Concatenate[_F, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], AwaitableResult[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] tapping failures.

    Applies an asynchronous side-effect function to [trcks.Failure][] values
    while returning the [trcks.Failure][] unchanged.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Asynchronous side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def log_err(err: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Error: {err}")
        ...
        >>> p = (
        ...     r.construct_failure("oops"),
        ...     r.tap_failure_to_awaitable(log_err),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        Error: oops
        ('failure', 'oops')
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (ar.construct_from_result, ar.tap_failure_to_awaitable(f, *args, **kwargs))
    )


def tap_failure_to_awaitable_result(
    f: Callable[Concatenate[_F, _P], AwaitableResult[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], AwaitableResult[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] tapping failures.

    Applies an asynchronous side-effect function returning [trcks.AwaitableResult][]
    to [trcks.Failure][] values while returning the [trcks.Result][] unchanged.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Asynchronous side-effect function returning [trcks.AwaitableResult][].
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def audit_failure(err: str) -> tuple:
        ...     await asyncio.sleep(0.001)
        ...     return "failure", err
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.tap_failure_to_awaitable_result(audit_failure),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        ('failure', 'error')
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (
            ar.construct_from_result,
            ar.tap_failure_to_awaitable_result(f, *args, **kwargs),
        )
    )


def tap_success_to_awaitable(
    f: Callable[Concatenate[_S, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], AwaitableResult[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] tapping successes.

    Applies an asynchronous side-effect function to [trcks.Success][] values
    while returning the [trcks.Success][] unchanged.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Asynchronous side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def write_slowly(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote {n}")
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.tap_success_to_awaitable(write_slowly),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        Wrote 42
        ('success', 42)
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (ar.construct_from_result, ar.tap_success_to_awaitable(f, *args, **kwargs))
    )


def tap_success_to_awaitable_result(
    f: Callable[Concatenate[_S, _P], AwaitableResult[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], AwaitableResult[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResult][] tapping successes.

    Applies an asynchronous side-effect function returning [trcks.AwaitableResult][]
    to [trcks.Success][] values while returning the [trcks.Result][] unchanged.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Asynchronous side-effect function returning [trcks.AwaitableResult][].
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResult][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def validate_slowly(n: int) -> tuple:
        ...     await asyncio.sleep(0.001)
        ...     return "success", n if n > 0 else "failure"
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.tap_success_to_awaitable_result(validate_slowly),
        ... )
        >>> a_rslt = pipe(p)
        >>> asyncio.run(a_rslt)
        ('success', 42)
    """
    from trcks.fp._monads import awaitable_result as ar

    return compose2(
        (
            ar.construct_from_result,
            ar.tap_success_to_awaitable_result(f, *args, **kwargs),
        )
    )


def map_failure_to_iterable(
    f: Callable[Concatenate[_F1, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S]], ResultTuple[_F1, _S]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] mapping failures.

    Applies a function to [trcks.Failure][] values.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def duplicate(x: str) -> tuple[str, ...]:
        ...     return (x, x)
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.map_failure_to_iterable(duplicate),
        ... )
        >>> r_tpl = pipe(p)
        >>> r_tpl
        ('success', ('error', 'error'))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (rt.construct_from_result, rt.map_failure_to_iterable(f, *args, **kwargs))
    )


def map_failure_to_result_iterable(
    f: Callable[Concatenate[_F1, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S]], ResultTuple[_F1, _S]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] mapping failures.

    Applies a function to [trcks.Failure][] values.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def duplicate_err(x: str) -> tuple:
        ...     return "success", (x, x)
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.map_failure_to_result_iterable(duplicate_err),
        ... )
        >>> r_tpl = pipe(p)
        >>> r_tpl
        ('success', ('error', 'error'))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (
            rt.construct_from_result,
            rt.map_failure_to_result_iterable(f, *args, **kwargs),
        )
    )


def map_success_to_iterable(
    f: Callable[Concatenate[_S1, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S1]], ResultTuple[_F, _S1]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] mapping successes.

    Applies a function to [trcks.Success][] values.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def duplicate(x: int) -> tuple[int, ...]:
        ...     return (x, x)
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.map_success_to_iterable(duplicate),
        ... )
        >>> r_tpl = pipe(p)
        >>> r_tpl
        ('success', (42, 42))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (rt.construct_from_result, rt.map_successes_to_iterable(f, *args, **kwargs))
    )


def map_success_to_result_iterable(
    f: Callable[Concatenate[_S1, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S1]], ResultTuple[_F, _S1]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] mapping successes.

    Applies a function to [trcks.Success][] values.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def duplicate(x: int) -> tuple:
        ...     return "success", (x, x)
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.map_success_to_result_iterable(duplicate),
        ... )
        >>> r_tpl = pipe(p)
        >>> r_tpl
        ('success', (42, 42))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (
            rt.construct_from_result,
            rt.map_successes_to_result_iterable(f, *args, **kwargs),
        )
    )


def tap_failure_to_iterable(
    f: Callable[Concatenate[_F, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], ResultTuple[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] tapping failures.

    Applies a side-effect function to [trcks.Failure][] values
    while returning the [trcks.Failure][] unchanged.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def log_err(err: str) -> tuple[str, ...]:
        ...     print(f"Error: {err}")
        ...     return (err,)
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.tap_failure_to_iterable(log_err),
        ... )
        >>> r_tpl = pipe(p)
        Error: error
        >>> r_tpl
        ('success', ('error',))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (rt.construct_from_result, rt.tap_failure_to_iterable(f, *args, **kwargs))
    )


def tap_failure_to_result_iterable(
    f: Callable[Concatenate[_F, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], ResultTuple[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] tapping failures.

    Applies a side-effect function to [trcks.Failure][] values
    while returning the [trcks.Failure][] unchanged.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def log_err(err: str) -> tuple:
        ...     print(f"Error: {err}")
        ...     return "failure", (err,)
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.tap_failure_to_result_iterable(log_err),
        ... )
        >>> r_tpl = pipe(p)
        Error: error
        >>> r_tpl
        ('failure', 'error')
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (
            rt.construct_from_result,
            rt.tap_failure_to_result_iterable(f, *args, **kwargs),
        )
    )


def tap_success_to_iterable(
    f: Callable[Concatenate[_S, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], ResultTuple[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] tapping successes.

    Applies a side-effect function to [trcks.Success][] values
    while returning the [trcks.Success][] unchanged.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def log_mult(n: int) -> tuple[None, ...]:
        ...     print(f"v={n}")
        ...     print(f"v={n}")
        ...     return None, None
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.tap_success_to_iterable(log_mult),
        ... )
        >>> r_tpl = pipe(p)
        v=42
        v=42
        >>> r_tpl
        ('success', (42, 42))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (rt.construct_from_result, rt.tap_successes_to_iterable(f, *args, **kwargs))
    )


def tap_success_to_result_iterable(
    f: Callable[Concatenate[_S, _P], object],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], ResultTuple[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.ResultTuple][] tapping successes.

    Applies a side-effect function to [trcks.Success][] values
    while returning the [trcks.Success][] unchanged.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.ResultTuple][].

    Example:
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> def log_mult(n: int) -> tuple:
        ...     print(f"v={n}")
        ...     print(f"v={n}")
        ...     return "success", (None, None)
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.tap_success_to_result_iterable(log_mult),
        ... )
        >>> r_tpl = pipe(p)
        v=42
        v=42
        >>> r_tpl
        ('success', (42, 42))
    """
    from trcks.fp._monads import result_tuple as rt

    return compose2(
        (
            rt.construct_from_result,
            rt.tap_successes_to_result_iterable(f, *args, **kwargs),
        )
    )


def map_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S]], AwaitableResultTuple[_F1, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResultTuple][] mapping failures.

    Applies an asynchronous function to [trcks.Failure][] values.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Failure][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResultTuple][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def duplicate_slowly(err: str) -> tuple[str, ...]:
        ...     await asyncio.sleep(0.001)
        ...     return (err, err)
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.map_failure_to_awaitable_result_iterable(duplicate_slowly),
        ... )
        >>> a_r_tpl = pipe(p)
        >>> asyncio.run(a_r_tpl)
        ('success', ('error', 'error'))
    """
    from trcks.fp._monads import awaitable_result_tuple as art

    return compose2(
        (
            art.construct_from_result,
            art.map_failure_to_awaitable_iterable(f, *args, **kwargs),
        )
    )


def map_success_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S1]], AwaitableResultTuple[_F, _S1]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResultTuple][] mapping successes.

    Applies an asynchronous function to [trcks.Success][] values.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.Success][] values.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResultTuple][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def duplicate_slowly(n: int) -> tuple[int, ...]:
        ...     await asyncio.sleep(0.001)
        ...     return (n, n)
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.map_success_to_awaitable_result_iterable(duplicate_slowly),
        ... )
        >>> a_r_tpl = pipe(p)
        >>> asyncio.run(a_r_tpl)
        ('success', (42, 42))
    """
    from trcks.fp._monads import awaitable_result_tuple as art

    return compose2(
        (
            art.construct_from_result,
            art.map_successes_to_awaitable_iterable(f, *args, **kwargs),
        )
    )


def tap_failure_to_awaitable_result_iterable(
    f: Callable[Concatenate[_F, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], AwaitableResultTuple[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResultTuple][] tapping failures.

    Applies an asynchronous side-effect function to [trcks.Failure][] values
    while returning the [trcks.Failure][] unchanged.
    [trcks.Success][] values are passed on unchanged.

    Args:
        f: Asynchronous side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResultTuple][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def audit_err(err: str) -> tuple[str, ...]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Audited {err}")
        ...     return (err, err)
        ...
        >>> p = (
        ...     r.construct_failure("error"),
        ...     r.tap_failure_to_awaitable_result_iterable(audit_err),
        ... )
        >>> a_r_tpl = pipe(p)
        >>> asyncio.run(a_r_tpl)
        Audited error
        ('success', ('error', 'error'))
    """
    from trcks.fp._monads import awaitable_result_tuple as art

    return compose2(
        (
            art.construct_from_result,
            art.tap_failure_to_awaitable_iterable(f, *args, **kwargs),
        )
    )


def tap_success_to_awaitable_result_iterable(
    f: Callable[Concatenate[_S, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F, _S]], AwaitableResultTuple[_F, _S]]:
    """Transition [trcks.Result][] to [trcks.AwaitableResultTuple][] tapping successes.

    Applies an asynchronous side-effect function to [trcks.Success][] values
    while returning the [trcks.Success][] unchanged.
    [trcks.Failure][] values are passed on unchanged.

    Args:
        f: Asynchronous side-effect function to apply.
        *args: Positional arguments to be passed to `f`.
        **kwargs: Keyword arguments to be passed to `f`.

    Returns:
        Function that transitions [trcks.Result][] to [trcks.AwaitableResultTuple][].

    Example:
        >>> import asyncio
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> async def log_mult(n: int) -> tuple[None, ...]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"v={n}")
        ...     print(f"v={n}")
        ...     return None, None
        ...
        >>> p = (
        ...     r.construct_success(42),
        ...     r.tap_success_to_awaitable_result_iterable(log_mult),
        ... )
        >>> a_r_tpl = pipe(p)
        >>> asyncio.run(a_r_tpl)
        v=42
        v=42
        ('success', (42, 42))
    """
    from trcks.fp._monads import awaitable_result_tuple as art

    return compose2(
        (
            art.construct_from_result,
            art.tap_successes_to_awaitable_iterable(f, *args, **kwargs),
        )
    )


# Re-assign __module__ for widening functions
for _name in __all__:
    if _name.startswith(("map", "tap")) and _name not in [
        "map_failure_to_result",
        "map_success_to_result",
        "tap_failure_to_result",
        "tap_success_to_result",
    ]:
        globals()[_name].__module__ = __name__
