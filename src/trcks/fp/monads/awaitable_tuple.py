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
    ...         at.construct_from_iterable((4, 2, 0)),
    ...         at.map_(double_integer),
    ...         at.tap(log_integer),
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
    ...         at.construct_from_iterable((1, 2, 3)),
    ...         at.map_to_awaitable_iterable(slowly_duplicate_integer),
    ...     )
    ...
    >>> asyncio.run(main())
    (1, 1, 2, 2, 3, 3)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import Never, TypeVar, deprecated
from trcks.fp._monads import awaitable_result_tuple as art
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
from trcks.fp.composition import compose

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks import (
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
    "construct_from_awaitable",
    "construct_from_awaitable_iterable",
    "construct_from_awaitable_tuple",
    "construct_from_iterable",
    "construct_from_tuple",
    "map_",
    "map_to_awaitable",
    "map_to_awaitable_iterable",
    "map_to_awaitable_result",
    "map_to_awaitable_result_iterable",
    "map_to_awaitable_result_tuple",
    "map_to_awaitable_tuple",
    "map_to_iterable",
    "map_to_result",
    "map_to_result_iterable",
    "map_to_result_tuple",
    "map_to_tuple",
    "tap",
    "tap_to_awaitable",
    "tap_to_awaitable_iterable",
    "tap_to_awaitable_result",
    "tap_to_awaitable_result_iterable",
    "tap_to_awaitable_result_tuple",
    "tap_to_awaitable_tuple",
    "tap_to_iterable",
    "tap_to_result",
    "tap_to_result_iterable",
    "tap_to_result_tuple",
    "tap_to_tuple",
    "to_coroutine_tuple",
]
__docformat__ = "google"

_F = TypeVar("_F")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


@deprecated("Use construct_from_awaitable_iterable instead")
def construct_from_awaitable_tuple(
    a_tpl: AwaitableTuple[_T],
) -> AwaitableTuple[_T]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.construct_from_awaitable_iterable][].
    """
    return construct_from_awaitable_iterable(a_tpl)  # pragma: no cover


@deprecated("Use construct_from_iterable instead")
def construct_from_tuple(tpl: tuple[_T, ...], /) -> AwaitableTuple[_T]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.construct_from_iterable][].
    """
    return construct_from_iterable(tpl)  # pragma: no cover


def map_to_awaitable_result(
    f: Callable[Concatenate[_T1, _P], AwaitableResult[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps each element of a [trcks.AwaitableTuple][]
    to a [trcks.AwaitableResult][] value.

    Args:
        f: Asynchronous function to apply to each element,
            returning a [trcks.AwaitableResult][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a [trcks.SuccessTuple][] if the function returns [trcks.Success][]
                for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_double_if_positive(n: int) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", n * 2
        ...     return "failure", "negative"
        ...
        >>> double_if_positive = (
        ...     at.map_to_awaitable_result(slowly_double_if_positive)
        ... )
        >>> a_r_tpl_1 = double_if_positive(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = double_if_positive(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.map_successes_to_awaitable_result(f, *args, **kwargs),
    )
    return compose(*c)


def map_to_awaitable_result_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps each element of a [trcks.AwaitableTuple][]
    to a [trcks.AwaitableResultIterable][] and flattens the result.

    Args:
        f: Asynchronous function to apply to each element,
            returning a [trcks.AwaitableResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a flattened [trcks.SuccessTuple][] if the function returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_expand_if_positive(n: int) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", (n, -n)
        ...     return "failure", "negative"
        ...
        >>> expand_if_positive = (
        ...     at.map_to_awaitable_result_iterable(slowly_expand_if_positive)
        ... )
        >>> a_r_tpl_1 = expand_if_positive(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, -1, 2, -2))
        >>> a_r_tpl_2 = expand_if_positive(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.map_successes_to_awaitable_result_iterable(f, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use map_to_awaitable_result_iterable instead")
def map_to_awaitable_result_tuple(
    f: Callable[Concatenate[_T1, _P], AwaitableResultTuple[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _S]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.map_to_awaitable_result_iterable][].
    """
    return map_to_awaitable_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_to_awaitable_iterable instead")
def map_to_awaitable_tuple(
    f: Callable[Concatenate[_T1, _P], AwaitableTuple[_T2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.map_to_awaitable_iterable][].
    """
    return map_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


def map_to_result(
    f: Callable[Concatenate[_T1, _P], Result[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps each element of a [trcks.AwaitableTuple][]
    to a [trcks.Result][] value.

    Args:
        f: Synchronous function to apply to each element,
            returning a [trcks.Result][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a [trcks.SuccessTuple][] with all transformed elements if the
                function returns [trcks.Success][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def double_if_positive(n: int) -> Result[str, int]:
        ...     if n > 0:
        ...         return "success", n * 2
        ...     return "failure", "negative"
        ...
        >>> double_result = at.map_to_result(double_if_positive)
        >>> a_r_tpl_1 = double_result(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = double_result(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.map_successes_to_result(f, *args, **kwargs),
    )
    return compose(*c)


def map_to_result_iterable(
    f: Callable[Concatenate[_T1, _P], ResultIterable[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _S]]:
    """Create function that maps each element of a [trcks.AwaitableTuple][]
    to a [trcks.ResultIterable][] and flattens the result.

    Args:
        f: Synchronous function to apply to each element,
            returning a [trcks.ResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - the first [trcks.Failure][] returned by the function, or
            - a flattened [trcks.SuccessTuple][] if the function returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def expand_if_positive(n: int) -> ResultTuple[str, int]:
        ...     if n > 0:
        ...         return "success", (n, -n)
        ...     return "failure", "negative"
        ...
        >>> expand_result = at.map_to_result_iterable(expand_if_positive)
        >>> a_r_tpl_1 = expand_result(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, -1, 2, -2))
        >>> a_r_tpl_2 = expand_result(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _S]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.map_successes_to_result_iterable(f, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use map_to_result_iterable instead")
def map_to_result_tuple(
    f: Callable[Concatenate[_T1, _P], ResultTuple[_F, _S]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _S]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.map_to_result_iterable][].
    """
    return map_to_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_to_iterable instead")
def map_to_tuple(
    f: Callable[Concatenate[_T1, _P], tuple[_T2, ...]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T2]]:
    """Deprecated alias for [trcks.fp.monads.awaitable_tuple.map_to_iterable][]."""
    return map_to_iterable(f, *args, **kwargs)  # pragma: no cover


def tap_to_awaitable_result(
    f: Callable[Concatenate[_T1, _P], AwaitableResult[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][]
    to each element of a [trcks.AwaitableTuple][].

    Args:
        f: Asynchronous side effect to apply to each element,
            returning a [trcks.AwaitableResult][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* elements if the applied side effect returns
                [trcks.Success][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_check_if_positive(n: int) -> Result[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", None
        ...     return "failure", "negative"
        ...
        >>> check_if_positive = at.tap_to_awaitable_result(slowly_check_if_positive)
        >>> a_r_tpl_1 = check_if_positive(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = check_if_positive(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.tap_successes_to_awaitable_result(f, *args, **kwargs),
    )
    return compose(*c)


def tap_to_awaitable_result_iterable(
    f: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResultIterable][]
    to each element of a [trcks.AwaitableTuple][].

    Args:
        f: Asynchronous side effect to apply to each element,
            returning a [trcks.AwaitableResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* elements with each element repeated once
                per side effect output element if the applied side effect returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> async def slowly_audit(n: int) -> ResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "negative"
        ...
        >>> audit_successes = at.tap_to_awaitable_result_iterable(slowly_audit)
        >>> a_r_tpl_1 = audit_successes(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = audit_successes(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.tap_successes_to_awaitable_result_iterable(f, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use tap_to_awaitable_result_iterable instead")
def tap_to_awaitable_result_tuple(
    f: Callable[Concatenate[_T1, _P], AwaitableResultTuple[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.tap_to_awaitable_result_iterable][].
    """
    return tap_to_awaitable_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_to_awaitable_iterable instead")
def tap_to_awaitable_tuple(
    f: Callable[Concatenate[_T1, _P], AwaitableTuple[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.tap_to_awaitable_iterable][].
    """
    return tap_to_awaitable_iterable(f, *args, **kwargs)  # pragma: no cover


def tap_to_result(
    f: Callable[Concatenate[_T1, _P], Result[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.Result][]
    to each element of a [trcks.AwaitableTuple][].

    Args:
        f: Synchronous side effect to apply to each element,
            returning a [trcks.Result][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* elements if the applied side effect returns
                [trcks.Success][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def check_if_positive(n: int) -> Result[str, None]:
        ...     if n > 0:
        ...         return "success", None
        ...     return "failure", "negative"
        ...
        >>> check_if_positive_sync = at.tap_to_result(check_if_positive)
        >>> a_r_tpl_1 = check_if_positive_sync(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = check_if_positive_sync(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.tap_successes_to_result(f, *args, **kwargs),
    )
    return compose(*c)


def tap_to_result_iterable(
    f: Callable[Concatenate[_T1, _P], ResultIterable[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.ResultIterable][]
    to each element of a [trcks.AwaitableTuple][].

    Args:
        f: Synchronous side effect to apply to each element,
            returning a [trcks.ResultIterable][].
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Maps [trcks.AwaitableTuple][]s to [trcks.AwaitableResultTuple][]s with

            - *the returned* [trcks.Failure][] if the applied side effect returns
                a [trcks.Failure][] for an element, or
            - *the original* elements with each element repeated once
                per side effect output element if the applied side effect returns
                [trcks.SuccessTuple][] for all elements.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> def audit(n: int) -> ResultTuple[str, None]:
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "negative"
        ...
        >>> audit_successes_sync = at.tap_to_result_iterable(audit)
        >>> a_r_tpl_1 = audit_successes_sync(at.construct_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = audit_successes_sync(at.construct_from_iterable((1, -1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
    """
    c: tuple[
        Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[Never, _T1]],
        Callable[[AwaitableResultTuple[Never, _T1]], AwaitableResultTuple[_F, _T1]],
    ] = (
        art.construct_successes_from_awaitable_iterable,
        art.tap_successes_to_result_iterable(f, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use tap_to_result_iterable instead")
def tap_to_result_tuple(
    f: Callable[Concatenate[_T1, _P], ResultTuple[_F, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableResultTuple[_F, _T1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_tuple.tap_to_result_iterable][].
    """
    return tap_to_result_iterable(f, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_to_iterable instead")
def tap_to_tuple(
    f: Callable[Concatenate[_T1, _P], tuple[object, ...]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableTuple[_T1]], AwaitableTuple[_T1]]:
    """Deprecated alias for [trcks.fp.monads.awaitable_tuple.tap_to_iterable][]."""
    return tap_to_iterable(f, *args, **kwargs)  # pragma: no cover
