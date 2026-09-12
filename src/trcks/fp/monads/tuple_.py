"""Monadic functions for homogeneous [tuple][]s.

Provides utilities for functional composition of functions
returning homogeneous [tuple][] values.

Note:
    The underscore in the module name helps to avoid collisions
    with the built-in class [tuple][].

Examples:
    Create and process a homogeneous [tuple][]:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import tuple_ as t
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> tpl = pipe(
    ...     (
    ...         (1, 2, 3),
    ...         t.map_(double_integer),
    ...         t.tap(log_integer),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> tpl
    (2, 4, 6)

    Map each element to a homogeneous tuple and flatten the result:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import tuple_ as t
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> tpl = pipe(
    ...     (
    ...         (1, 2, 3),
    ...         t.map_to_iterable(duplicate_integer),
    ...     )
    ... )
    >>> tpl
    (1, 1, 2, 2, 3, 3)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import Never, TypeVar, deprecated
from trcks.fp._monads import awaitable_result_tuple as art
from trcks.fp._monads import awaitable_tuple as at
from trcks.fp._monads import result_tuple as rt
from trcks.fp._monads.tuple_ import (
    construct,
    map_,
    map_to_iterable,
    tap,
    tap_to_iterable,
)
from trcks.fp.composition import compose2

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from trcks import (
        AwaitableIterable,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        AwaitableTuple,
        Result,
        ResultIterable,
        ResultTuple,
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
    "map_to_tuple",
    "tap",
    "tap_to_awaitable",
    "tap_to_awaitable_iterable",
    "tap_to_awaitable_result",
    "tap_to_awaitable_result_iterable",
    "tap_to_iterable",
    "tap_to_result",
    "tap_to_result_iterable",
    "tap_to_tuple",
]
__docformat__ = "google"

_F = TypeVar("_F")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def map_to_awaitable(
    f: Callable[Concatenate[_T1, _P], Awaitable[_T2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableTuple[_T2]]:
    """Create function that maps each element of a homogeneous [tuple][]
    to a new element of a [trcks.AwaitableTuple][].

    Args:
        f: Asynchronous function to apply to each element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.AwaitableTuple][]s of the same length
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def slowly_add_one(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n + 1
        ...
        >>> add_one_to_each = t.map_to_awaitable(slowly_add_one)
        >>> a_tpl = add_one_to_each((1, 2, 3))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (2, 3, 4)
    """
    return compose2(
        (at.construct_from_iterable, at.map_to_awaitable(f, *args, **kwargs))
    )


def map_to_awaitable_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableIterable[_T2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableTuple[_T2]]:
    """Create function that maps each element of a homogeneous [tuple][]
    to a [trcks.AwaitableIterable][] and flattens the result.

    Args:
        f: Asynchronous function to apply to each element,
            returning a [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.AwaitableTuple][]s of varying length
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def slowly_duplicate(n: int) -> tuple[int, int]:
        ...     await asyncio.sleep(0.001)
        ...     return n, n
        ...
        >>> duplicate_each = t.map_to_awaitable_iterable(slowly_duplicate)
        >>> a_tpl = duplicate_each((1, 2))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (1, 1, 2, 2)
    """
    return compose2(
        (at.construct_from_iterable, at.map_to_awaitable_iterable(f, *args, **kwargs))
    )


def map_to_awaitable_result(
    f: Callable[Concatenate[_T1, _P], AwaitableResult[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps each element of a homogeneous [tuple][]
    to a [trcks.AwaitableResult][] value.

    Args:
        f: Asynchronous function to apply to each element,
            returning a [trcks.AwaitableResult][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.AwaitableResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a [trcks.SuccessTuple][] if the function returns [trcks.Success][]
                for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def slowly_double_if_positive(n: int) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", n * 2
        ...     return "failure", "negative"
        ...
        >>> double_if_positive = t.map_to_awaitable_result(slowly_double_if_positive)
        >>> a_r_tpl_1 = double_if_positive((1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = double_if_positive((1, -1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_iterable,
        art.map_successes_to_awaitable_result(f, *args, **kwargs),
    )
    return compose2(c)


def map_to_awaitable_result_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps each element of a homogeneous [tuple][]
    to a [trcks.AwaitableResultIterable][] and flattens the result.

    Args:
        f: Asynchronous function to apply to each element,
            returning a [trcks.AwaitableResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.AwaitableResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a flattened [trcks.SuccessTuple][] if the function returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def slowly_expand_if_positive(n: int) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", (n, -n)
        ...     return "failure", "negative"
        ...
        >>> expand_if_positive = (
        ...     t.map_to_awaitable_result_iterable(slowly_expand_if_positive)
        ... )
        >>> a_r_tpl_1 = expand_if_positive((1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, -1, 2, -2))
        >>> a_r_tpl_2 = expand_if_positive((1, -1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_iterable,
        art.map_successes_to_awaitable_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def map_to_result(
    f: Callable[Concatenate[_T1, _P], Result[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], ResultTuple[_F, _S]]:
    """Create function that maps each element of a homogeneous [tuple][]
    to a [trcks.Result][] value.

    Args:
        f: Synchronous function to apply to each element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.ResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a [trcks.SuccessTuple][] with all transformed elements if the
                function returns [trcks.Success][] for all elements.

    Examples:
        >>> from trcks import Result
        >>> from trcks.fp.monads import tuple_ as t
        >>> def double_if_positive(n: int) -> Result[str, int]:
        ...     if n > 0:
        ...         return "success", n * 2
        ...     return "failure", "negative"
        ...
        >>> double_if_positive_tuple = t.map_to_result(double_if_positive)
        >>> double_if_positive_tuple((1, 2, 3))
        ('success', (2, 4, 6))
        >>> double_if_positive_tuple((1, -1, 2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], ResultTuple[Never, _T1]],
        Callable[[ResultTuple[Never, _T1]], ResultTuple[_F, _S]],
    ] = (
        rt.construct_successes_from_iterable,
        rt.map_successes_to_result(f, *args, **kwargs),
    )
    return compose2(c)


def map_to_result_iterable(
    f: Callable[Concatenate[_T1, _P], ResultIterable[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], ResultTuple[_F, _S]]:
    """Create function that maps each element of a homogeneous [tuple][]
    to a [trcks.ResultIterable][] and flattens the result.

    Args:
        f: Synchronous function to apply to each element,
            returning a [trcks.ResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.ResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a flattened [trcks.SuccessTuple][] if the function returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import tuple_ as t
        >>> def expand_if_positive(n: int) -> ResultTuple[str, int]:
        ...     if n > 0:
        ...         return "success", (n, -n)
        ...     return "failure", "negative"
        ...
        >>> expand_if_positive_tuple = t.map_to_result_iterable(expand_if_positive)
        >>> expand_if_positive_tuple((1, 2))
        ('success', (1, -1, 2, -2))
        >>> expand_if_positive_tuple((1, -1, 2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], ResultTuple[Never, _T1]],
        Callable[[ResultTuple[Never, _T1]], ResultTuple[_F, _S]],
    ] = (
        rt.construct_successes_from_iterable,
        rt.map_successes_to_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


@deprecated("Use map_to_iterable instead")
def map_to_tuple(
    f: Callable[Concatenate[_T1, _P], tuple[_T2, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], tuple[_T2, ...]]:
    """Deprecated alias for [trcks.fp.monads.tuple_.map_to_iterable][]."""
    return map_to_iterable(f, *args, **kwargs)  # pragma: no cover


def tap_to_awaitable(
    f: Callable[Concatenate[_T1, _P], Awaitable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableTuple[_T1]]:
    """Create function that applies an asynchronous side effect
    to each element of a homogeneous [tuple][].

    Args:
        f: Asynchronous side effect to apply to each element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to each element of a homogeneous [tuple][] and
            returns a [trcks.AwaitableTuple][] of the original elements.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def slowly_log_integer(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Received: {n}")
        ...
        >>> log_each = t.tap_to_awaitable(slowly_log_integer)
        >>> a_tpl = log_each((1, 2, 3))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        Received: 1
        Received: 2
        Received: 3
        (1, 2, 3)
    """
    return compose2(
        (at.construct_from_iterable, at.tap_to_awaitable(f, *args, **kwargs))
    )


def tap_to_awaitable_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableIterable[object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableTuple[_T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableIterable][]
    to each element of a homogeneous [tuple][].

    Args:
        f: Asynchronous side effect to apply to each element,
            returning a [trcks.AwaitableIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to each element of a homogeneous [tuple][] and
            returns a [trcks.AwaitableTuple][] of the original elements,
            each repeated once per element in the side effect output.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def write_to_disk(n: int) -> tuple[str, str]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote {n} to disk.")
        ...     return str(n), str(n)
        ...
        >>> write_each_to_disk = t.tap_to_awaitable_iterable(write_to_disk)
        >>> a_tpl = write_each_to_disk((1, 2, 3))
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        Wrote 1 to disk.
        Wrote 2 to disk.
        Wrote 3 to disk.
        (1, 1, 2, 2, 3, 3)
    """
    return compose2(
        (at.construct_from_iterable, at.tap_to_awaitable_iterable(f, *args, **kwargs))
    )


def tap_to_awaitable_result(
    f: Callable[Concatenate[_T1, _P], AwaitableResult[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.Result][]
    to each element of a homogeneous [tuple][].

    Args:
        f: Asynchronous side effect to apply to each element,
            returning a [trcks.Result][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* homogeneous [tuple][] if the applied side effect
                returns [trcks.Success][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def slowly_check_if_positive(n: int) -> Result[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", None
        ...     return "failure", "negative"
        ...
        >>> check_if_positive = t.tap_to_awaitable_result(slowly_check_if_positive)
        >>> a_r_tpl_1 = check_if_positive((1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = check_if_positive((1, -1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_iterable,
        art.tap_successes_to_awaitable_result(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_awaitable_result_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResultIterable][]
    to each element of a homogeneous [tuple][].

    Args:
        f: Asynchronous side effect to apply to each element,
            returning a [trcks.AwaitableResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* homogeneous [tuple][] with each element repeated once
                per side effect output element if the applied side effect returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import tuple_ as t
        >>> async def audit(n: int) -> ResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "negative"
        ...
        >>> audit_successes = t.tap_to_awaitable_result_iterable(audit)
        >>> a_r_tpl_1 = audit_successes((1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = audit_successes((1, -1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_iterable,
        art.tap_successes_to_awaitable_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_result(
    f: Callable[Concatenate[_T1, _P], Result[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], ResultTuple[_F, _T1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.Result][]
    to each element of a homogeneous [tuple][].

    Args:
        f: Synchronous side effect to apply to each element.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.ResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* homogeneous [tuple][] if the applied side effect
                returns [trcks.Success][] for all elements.

    Examples:
        >>> from trcks import Result
        >>> from trcks.fp.monads import tuple_ as t
        >>> def audit(n: int) -> Result[str, None]:
        ...     if n > 0:
        ...         return "success", None
        ...     return "failure", "negative"
        ...
        >>> audit_successes = t.tap_to_result(audit)
        >>> audit_successes((1, 2))
        ('success', (1, 2))
        >>> audit_successes((1, -1, 2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], ResultTuple[Never, _T1]],
        Callable[[ResultTuple[Never, _T1]], ResultTuple[_F, _T1]],
    ] = (
        rt.construct_successes_from_iterable,
        rt.tap_successes_to_result(f, *args, **kwargs),
    )
    return compose2(c)


def tap_to_result_iterable(
    f: Callable[Concatenate[_T1, _P], ResultIterable[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], ResultTuple[_F, _T1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.ResultIterable][]
    to each element of a homogeneous [tuple][].

    Args:
        f: Synchronous side effect to apply to each element,
            returning a [trcks.ResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps homogeneous [tuple][]s to [trcks.ResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* homogeneous [tuple][] with each element repeated once
                per side effect output element if the applied side effect returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import tuple_ as t
        >>> def audit(n: int) -> ResultTuple[str, None]:
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "negative"
        ...
        >>> audit_successes = t.tap_to_result_iterable(audit)
        >>> audit_successes((7,))
        ('success', (7, 7))
        >>> audit_successes((1, -1))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[tuple[_T1, ...]], ResultTuple[Never, _T1]],
        Callable[[ResultTuple[Never, _T1]], ResultTuple[_F, _T1]],
    ] = (
        rt.construct_successes_from_iterable,
        rt.tap_successes_to_result_iterable(f, *args, **kwargs),
    )
    return compose2(c)


@deprecated("Use tap_to_iterable instead")
def tap_to_tuple(
    f: Callable[Concatenate[_T1, _P], tuple[object, ...]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[tuple[_T1, ...]], tuple[_T1, ...]]:
    """Deprecated alias for [trcks.fp.monads.tuple_.tap_to_iterable][]."""
    return tap_to_iterable(f, *args, **kwargs)  # pragma: no cover
