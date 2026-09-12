"""Monadic functions for [collections.abc.Awaitable][].

Provides utilities for functional composition of asynchronous functions.

Examples:
    >>> import asyncio
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable as a
    >>> async def read_from_disk() -> str:
    ...     await asyncio.sleep(0.001)
    ...     return "Hello, world!"
    ...
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    ...
    >>> async def write_to_disk(s: str) -> None:
    ...     await asyncio.sleep(0.001)
    ...
    >>> async def main() -> str:
    ...     awaitable_str = read_from_disk()
    ...     return await pipe(
    ...         (
    ...             awaitable_str,
    ...             a.tap(lambda s: print(f"Read '{s}' from disk.")),
    ...             a.map_(transform),
    ...             a.tap_to_awaitable(write_to_disk),
    ...             a.tap(lambda s: print(f"Wrote '{s}' to disk.")),
    ...         ),
    ...     )
    ...
    >>> output = asyncio.run(main())
    Read 'Hello, world!' from disk.
    Wrote 'Length: 13' to disk.
    >>> output
    'Length: 13'
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import Never, TypeVar
from trcks.fp._monads import awaitable_result as ar
from trcks.fp._monads import awaitable_result_tuple as art
from trcks.fp._monads import awaitable_tuple as at
from trcks.fp._monads.awaitable import (
    construct,
    map_,
    map_to_awaitable,
    tap,
    tap_to_awaitable,
    to_coroutine,
)
from trcks.fp.composition import compose2

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableIterable,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        AwaitableTuple,
        Result,
        ResultIterable,
    )

__all__ = [
    "construct",
    "map_",
    "map_to_awaitable",
    "map_to_awaitable_iterable",
    "map_to_awaitable_result",
    "map_to_awaitable_result_iterable",
    "map_to_iterable",
    "map_to_result",
    "map_to_result_iterable",
    "tap",
    "tap_to_awaitable",
    "tap_to_awaitable_iterable",
    "tap_to_awaitable_result",
    "tap_to_awaitable_result_iterable",
    "tap_to_iterable",
    "tap_to_result",
    "tap_to_result_iterable",
    "to_coroutine",
]
__docformat__ = "google"

_F = TypeVar("_F")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def map_to_awaitable_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableIterable[_T2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableTuple[_T2]]:
    """Create function that maps the value of an [collections.abc.Awaitable][]
    to a [trcks.AwaitableIterable][] and flattens the result.

    Args:
        f: Asynchronous function to apply to the awaited value,
            returning a [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableTuple][]s
            of varying length according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_duplicate(n: int) -> tuple[int, ...]:
        ...     await asyncio.sleep(0.001)
        ...     return (n, n)
        ...
        >>> duplicate = a.map_to_awaitable_iterable(slowly_duplicate)
        >>> a_tpl = duplicate(a.construct(21))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (21, 21)
    """
    return compose2(
        (at.construct_from_awaitable, at.map_to_awaitable_iterable(f, *args, **kwargs))
    )


def map_to_awaitable_result(
    f: Callable[Concatenate[_T1, _P], AwaitableResult[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResult[_F, _S]]:
    """Create function that maps the value of an [collections.abc.Awaitable][]
    to a [trcks.AwaitableResult][] value.

    Args:
        f: Asynchronous function to apply to the awaited value,
            returning a [trcks.AwaitableResult][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResult][]s
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> async def slowly_assert_non_negative(
        ...     x: float,
        ... ) -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", x
        ...
        >>> assert_non_negative = a.map_to_awaitable_result(
        ...     slowly_assert_non_negative
        ... )
        >>> a_rslt = assert_non_negative(a.construct(42.0))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('success', 42.0)
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResult[Never, _T1]],
        Callable[[AwaitableResult[Never, _T1]], AwaitableResult[_F, _S]],
    ] = (
        ar.construct_success_from_awaitable,
        ar.map_success_to_awaitable_result(f, *args, **kwargs),
    )
    return compose2(c)


def map_to_awaitable_result_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps the value of an [collections.abc.Awaitable][]
    to a [trcks.AwaitableResultIterable][] and flattens the result.

    Args:
        f: Asynchronous function to apply to the awaited value,
            returning a [trcks.AwaitableResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResultTuple][]s with

            - the [trcks.Failure][] returned by the function, or
            - a [trcks.SuccessTuple][] containing the elements of
                the [trcks.SuccessIterable][] returned by the function.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def validate(x: float) -> AwaitableResultTuple[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", (x, x * 2)
        ...
        >>> validate_value = a.map_to_awaitable_result_iterable(validate)
        >>> a_r_tpl = validate_value(a.construct(5.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (5.0, 10.0))
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_awaitable,
        art.map_successes_to_awaitable_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def map_to_iterable(
    f: Callable[Concatenate[_T1, _P], Iterable[_T2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableTuple[_T2]]:
    """Create function that maps the value of an [collections.abc.Awaitable][]
    to a [collections.abc.Iterable][] and flattens the result.

    Args:
        f: Synchronous function to apply to the awaited value,
            returning a [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableTuple][]s
            of varying length according to the given function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> duplicate_with_negative = a.map_to_iterable(lambda n: (n, -n))
        >>> a_tpl = duplicate_with_negative(a.construct(3))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (3, -3)
    """
    return compose2(
        (at.construct_from_awaitable, at.map_to_iterable(f, *args, **kwargs))
    )


def map_to_result(
    f: Callable[Concatenate[_T1, _P], Result[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResult[_F, _S]]:
    """Create function that maps the value of an [collections.abc.Awaitable][]
    to a [trcks.Result][] value.

    Args:
        f: Synchronous function to apply to the awaited value,
            returning a [trcks.Result][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResult][]s
            according to the given function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> assert_non_negative = a.map_to_result(
        ...     lambda n: (
        ...         ("success", n) if n >= 0 else ("failure", "negative value")
        ...     )
        ... )
        >>> a_rslt = assert_non_negative(a.construct(-1))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('failure', 'negative value')
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResult[Never, _T1]],
        Callable[[AwaitableResult[Never, _T1]], AwaitableResult[_F, _S]],
    ] = (
        ar.construct_success_from_awaitable,
        ar.map_success_to_result(f, *args, **kwargs),
    )
    return compose2(c)


def map_to_result_iterable(
    f: Callable[Concatenate[_T1, _P], ResultIterable[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps the value of an [collections.abc.Awaitable][]
    to a [trcks.ResultIterable][] and flattens the result.

    Args:
        f: Synchronous function to apply to the awaited value,
            returning a [trcks.ResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResultTuple][]s with

            - the [trcks.Failure][] returned by the function, or
            - a [trcks.SuccessTuple][] containing the elements of
                the [trcks.SuccessIterable][] returned by the function.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def validate(x: float) -> ResultTuple[str, float]:
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", (x, x * 2)
        ...
        >>> validate_value = a.map_to_result_iterable(validate)
        >>> a_r_tpl = validate_value(a.construct(5.0))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (5.0, 10.0))
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_awaitable,
        art.map_successes_to_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_awaitable_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableIterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableTuple[_T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableIterable][]
    to the value of an [collections.abc.Awaitable][].

    Args:
        f: Asynchronous side effect to apply to the awaited value,
            returning a [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableTuple][]s with
            the original awaited value repeated once per element
            in the side effect output.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_duplicate_with_log(n: int) -> tuple[int, ...]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Processing: {n}")
        ...     return (n, n)
        ...
        >>> process_and_duplicate = a.tap_to_awaitable_iterable(
        ...     slowly_duplicate_with_log
        ... )
        >>> a_tpl = process_and_duplicate(a.construct(21))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        Processing: 21
        (21, 21)
    """
    return compose2(
        (at.construct_from_awaitable, at.tap_to_awaitable_iterable(f, *args, **kwargs))
    )


def tap_to_awaitable_result(
    f: Callable[Concatenate[_T1, _P], AwaitableResult[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResult[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][]
    to the value of an [collections.abc.Awaitable][].

    Args:
        f: Asynchronous side effect to apply to the awaited value,
            returning a [trcks.AwaitableResult][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResult][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][], or
            - *the original* awaited value as [trcks.AwaitableSuccess][]
                if the applied side effect returns [trcks.Success][].

    Examples:
        >>> import asyncio
        >>> from typing import Literal
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> WriteErrorLiteral = Literal["write error"]
        >>> async def write_to_disk(s: str, path: str) -> Result[
        ...     WriteErrorLiteral, None
        ... ]:
        ...     if path != "output.txt":
        ...         return "failure", "write error"
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' to file {path}.")
        ...     return "success", None
        ...
        >>> tap_write_to_error_file = a.tap_to_awaitable_result(
        ...     write_to_disk,
        ...     "error.txt",
        ... )
        >>> a_rslt_1 = tap_write_to_error_file(a.construct("Hello, world!"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'write error')
        >>> tap_write_to_output_file = a.tap_to_awaitable_result(
        ...     write_to_disk,
        ...     "output.txt",
        ... )
        >>> a_rslt_2 = tap_write_to_output_file(a.construct("Hello, world!"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        Wrote 'Hello, world!' to file output.txt.
        ('success', 'Hello, world!')
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResult[Never, _T1]],
        Callable[[AwaitableResult[Never, _T1]], AwaitableResult[_F, _T1]],
    ] = (
        ar.construct_success_from_awaitable,
        ar.tap_success_to_awaitable_result(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_awaitable_result_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResultIterable][]
    to the value of an [collections.abc.Awaitable][].

    Args:
        f: Asynchronous side effect to apply to the awaited value,
            returning a [trcks.AwaitableResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][], or
            - *the original* awaited value repeated once per element
                in the side effect output if the applied side effect returns
                [trcks.SuccessIterable][].

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def write_twice(s: str) -> AwaitableResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' twice.")
        ...     return "success", (None, None)
        ...
        >>> write_twice_tapped = a.tap_to_awaitable_result_iterable(write_twice)
        >>> a_r_tpl = write_twice_tapped(a.construct("Hello, world!"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Wrote 'Hello, world!' twice.
        ('success', ('Hello, world!', 'Hello, world!'))
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_awaitable,
        art.tap_successes_to_awaitable_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_iterable(
    f: Callable[Concatenate[_T1, _P], Iterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableTuple[_T1]]:
    """Create function that applies a synchronous side effect
    with return type [collections.abc.Iterable][]
    to the value of an [collections.abc.Awaitable][].

    Args:
        f: Synchronous side effect to apply to the awaited value,
            returning a [collections.abc.Iterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableTuple][]s with
            the original awaited value repeated once per element
            in the side effect output.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def duplicate_with_log(n: int) -> tuple[int, ...]:
        ...     print(f"Processing: {n}")
        ...     return (n, n)
        ...
        >>> process_and_duplicate = a.tap_to_iterable(duplicate_with_log)
        >>> a_tpl = process_and_duplicate(a.construct(42))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        Processing: 42
        (42, 42)
    """
    return compose2(
        (at.construct_from_awaitable, at.tap_to_iterable(f, *args, **kwargs))
    )


def tap_to_result(
    f: Callable[Concatenate[_T1, _P], Result[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResult[_F, _T1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.Result][]
    to the value of an [collections.abc.Awaitable][].

    Args:
        f: Synchronous side effect to apply to the awaited value,
            returning a [trcks.Result][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResult][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][], or
            - *the original* awaited value as [trcks.AwaitableSuccess][]
                if the applied side effect returns [trcks.Success][].

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> def print_positive_float(x: float) -> Result[str, None]:
        ...     if x <= 0:
        ...         return "failure", "not positive"
        ...     return "success", print(f"Positive float: {x}")
        ...
        >>> tap_positive_float = a.tap_to_result(print_positive_float)
        >>> a_rslt_1 = tap_positive_float(a.construct(-2.3))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not positive')
        >>> a_rslt_2 = tap_positive_float(a.construct(3.5))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        Positive float: 3.5
        ('success', 3.5)
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResult[Never, _T1]],
        Callable[[AwaitableResult[Never, _T1]], AwaitableResult[_F, _T1]],
    ] = (
        ar.construct_success_from_awaitable,
        ar.tap_success_to_result(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_result_iterable(
    f: Callable[Concatenate[_T1, _P], ResultIterable[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Awaitable[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.ResultIterable][]
    to the value of an [collections.abc.Awaitable][].

    Args:
        f: Synchronous side effect to apply to the awaited value,
            returning a [trcks.ResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [collections.abc.Awaitable][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][], or
            - *the original* awaited value repeated once per element
                in the side effect output if the applied side effect returns
                [trcks.SuccessIterable][].

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def write_twice(s: str) -> ResultTuple[str, None]:
        ...     print(f"Wrote '{s}' twice.")
        ...     return "success", (None, None)
        ...
        >>> write_twice_tapped = a.tap_to_result_iterable(write_twice)
        >>> a_r_tpl = write_twice_tapped(a.construct("Hello, world!"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Wrote 'Hello, world!' twice.
        ('success', ('Hello, world!', 'Hello, world!'))
    """
    c: tuple[
        Callable[[Awaitable[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_awaitable,
        art.tap_successes_to_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)
