"""Monadic functions for [trcks.AwaitableResultTuple][].

Provides utilities for functional composition of
asynchronous [trcks.ResultTuple][]-returning functions.

Example:
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

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, deprecated
from trcks.exceptions import TrcksTypeError
from trcks.fp.composition import compose2
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import result as r
from trcks.fp.monads import result_tuple as rt

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableFailure,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        AwaitableSuccessTuple,
        Result,
        ResultIterable,
        ResultTuple,
        SuccessTuple,
    )

__docformat__ = "google"

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def construct_failure(value: _F) -> AwaitableFailure[_F]:
    """Create a [trcks.AwaitableFailure][] object from a value.

    Args:
        value: Value to be wrapped in a [trcks.AwaitableFailure][] object.

    Returns:
        A new [trcks.AwaitableFailure][] instance containing the given value.

    Note:
        This function is equivalent to
            [trcks.fp.monads.awaitable_result.construct_failure][].

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_failure("not found")
        >>> isinstance(a_r_tpl, Awaitable)
        True
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('failure', 'not found')
    """
    return a.construct(rt.construct_failure(value))


def construct_failure_from_awaitable(awtbl: Awaitable[_F]) -> AwaitableFailure[_F]:
    """Create a [trcks.AwaitableFailure][] object
    from a [collections.abc.Awaitable][] object.

    Args:
        awtbl: [collections.abc.Awaitable][] object to be wrapped
            in a [trcks.AwaitableFailure][] object.

    Returns:
        A new [trcks.AwaitableFailure][] instance containing
            the value of the given [collections.abc.Awaitable][] object.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> awtbl = a.construct("not found")
        >>> a_r_tpl = art.construct_failure_from_awaitable(awtbl)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('failure', 'not found')
    """
    return a.map_(rt.construct_failure)(awtbl)


def construct_from_awaitable_result(
    a_rslt: AwaitableResult[_F, _S],
) -> AwaitableResultTuple[_F, _S]:
    """Create a [trcks.AwaitableResultTuple][] object
    from a [trcks.AwaitableResult][] object.

    The success payload is wrapped in a single-element tuple.

    Args:
        a_rslt: [trcks.AwaitableResult][] object to be converted.

    Returns:
        A new [trcks.AwaitableResultTuple][] instance where
            the success payload is wrapped in a single-element tuple,
            or the original failure is preserved.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_rslt_1 = ar.construct_success(7)
        >>> a_r_tpl_1 = art.construct_from_awaitable_result(a_rslt_1)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7,))
        >>> a_rslt_2 = ar.construct_failure("oops")
        >>> a_r_tpl_2 = art.construct_from_awaitable_result(a_rslt_2)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return a.map_(rt.construct_from_result)(a_rslt)


def construct_from_result(rslt: Result[_F, _S]) -> AwaitableResultTuple[_F, _S]:
    """Create a [trcks.AwaitableResultTuple][] object from a [trcks.Result][].

    The success payload is wrapped in a single-element tuple.

    Args:
        rslt: [trcks.Result][] object to be converted.

    Returns:
        A new [trcks.AwaitableResultTuple][] instance where
            the success payload is wrapped in a single-element tuple,
            or the original failure is preserved.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl_1 = art.construct_from_result(("success", 7))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7,))
        >>> a_r_tpl_2 = art.construct_from_result(("failure", "oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return a.construct(rt.construct_from_result(rslt))


def construct_from_result_tuple(
    r_tpl: ResultTuple[_F, _S],
) -> AwaitableResultTuple[_F, _S]:
    """Create a [trcks.AwaitableResultTuple][] object
    from a [trcks.ResultTuple][] object.

    Args:
        r_tpl: [trcks.ResultTuple][] object to be wrapped
            in a [trcks.AwaitableResultTuple][] object.

    Returns:
        A new [trcks.AwaitableResultTuple][] instance containing
            the given [trcks.ResultTuple][] object.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_from_result_tuple(("success", (1, 2)))
        >>> isinstance(a_r_tpl, Awaitable)
        True
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 2))
    """
    return a.construct(r_tpl)


def construct_successes(value: _S) -> AwaitableSuccessTuple[_S]:
    """Create a [trcks.AwaitableSuccessTuple][] object from a single value.

    Args:
        value: A single value.

    Returns:
        A new [trcks.AwaitableSuccessTuple][] instance containing
            the single value in a tuple.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_successes(42)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (42,))
    """
    return a.construct(rt.construct_successes(value))


def construct_successes_from_awaitable(
    awtbl: Awaitable[_S],
) -> AwaitableSuccessTuple[_S]:
    """Create a [trcks.AwaitableSuccessTuple][] object
    from a [collections.abc.Awaitable][] object.

    The value of the awaitable is wrapped in a single-element success tuple.

    Args:
        awtbl: [collections.abc.Awaitable][] object whose resolved value
            will be wrapped in a [trcks.AwaitableSuccessTuple][].

    Returns:
        A new [trcks.AwaitableSuccessTuple][] instance containing
            the value of the given [collections.abc.Awaitable][] in a tuple.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> awtbl = a.construct(7)
        >>> a_r_tpl = art.construct_successes_from_awaitable(awtbl)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (7,))
    """
    return a.map_(rt.construct_successes)(awtbl)


def construct_successes_from_tuple(
    tpl: tuple[_S, ...],
) -> AwaitableSuccessTuple[_S]:
    """Create a [trcks.AwaitableSuccessTuple][] object from a homogeneous tuple.

    Args:
        tpl: Homogeneous tuple to be wrapped in a [trcks.AwaitableSuccessTuple][].

    Returns:
        A new [trcks.AwaitableSuccessTuple][] instance containing
            the given homogeneous tuple.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_successes_from_tuple((1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 2))
    """
    return a.construct(rt.construct_successes_from_tuple(tpl))


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1]]:
    """Create function that maps [trcks.AwaitableFailure][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableFailure][] values
            according to the given function and
            leaves [trcks.AwaitableSuccessTuple][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _add_prefix(description: str) -> str:
        ...     return f"err: {description}"
        ...
        >>> add_prefix = art.map_failure(_add_prefix)
        >>> a_r_tpl_1 = add_prefix(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'err: not found')
        >>> a_r_tpl_2 = add_prefix(art.construct_successes_from_tuple((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure(f))


def map_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[_F2]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1]]:
    """Create function that maps [trcks.AwaitableFailure][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableFailure][] values
            according to the given asynchronous function and
            leaves [trcks.AwaitableSuccessTuple][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_add_prefix(s: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"err: {s}"
        ...
        >>> slowly_add_prefix = art.map_failure_to_awaitable(_slowly_add_prefix)
        >>> a_r_tpl_1 = slowly_add_prefix(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'err: not found')
        >>> a_r_tpl_2 = slowly_add_prefix(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return map_failure_to_awaitable_result_iterable(
        compose2((f, construct_failure_from_awaitable))
    )


def map_failure_to_awaitable_result_iterable(
    f: Callable[[_F1], AwaitableResultIterable[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResultTuple][] values.

    [trcks.AwaitableSuccessTuple][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to new
            [trcks.AwaitableResultTuple][] values
            according to the given asynchronous function and
            leaves [trcks.AwaitableSuccessTuple][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0,)
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = (
        ...     art.map_failure_to_awaitable_result_iterable(
        ...         _slowly_recover_from_not_found
        ...     )
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = slowly_recover_from_not_found(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """

    async def partially_mapped_f(
        r_tpl: ResultTuple[_F1, _S1],
    ) -> ResultTuple[_F2, _S1 | _S2]:
        match r_tpl:
            case ("failure", value):
                return r.map_success(tuple)(await f(value))  # pyrefly: ignore[bad-argument-type]
            case ("success", _):
                return r_tpl
            case _:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_tpl, "ResultTuple"
                )

    return a.map_to_awaitable(partially_mapped_f)


@deprecated("Use map_failure_to_awaitable_result_iterable instead")
def map_failure_to_awaitable_result_tuple(
    f: Callable[[_F1], AwaitableResultTuple[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_awaitable_result_iterable][].
    """
    return map_failure_to_awaitable_result_iterable(f)  # pragma: no cover


def map_failure_to_iterable(
    f: Callable[[_F1], Iterable[_S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [collections.abc.Iterable][]s.

    [trcks.AwaitableSuccessTuple][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [collections.abc.Iterable][]s
            wrapped in [trcks.AwaitableSuccessTuple][] values and
            leaves [trcks.AwaitableSuccessTuple][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> tuple[int, ...]:
        ...     if description == "not found":
        ...         return (0,)
        ...     return ()
        ...
        >>> recover_from_not_found = art.map_failure_to_iterable(
        ...     _recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', ())
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure_to_iterable(f))


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResultTuple][] values.

    [trcks.AwaitableSuccessTuple][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to new
            [trcks.AwaitableResultTuple][] values
            according to the given function and
            leaves [trcks.AwaitableSuccessTuple][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> Result[str, int]:
        ...     if description == "not found":
        ...         return "success", 0
        ...     return "failure", description
        ...
        >>> recover_from_not_found = art.map_failure_to_result(_recover_from_not_found)
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure_to_result(f))


def map_failure_to_result_iterable(
    f: Callable[[_F1], ResultIterable[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResultTuple][] values.

    [trcks.AwaitableSuccessTuple][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to new
            [trcks.AwaitableResultTuple][] values
            according to the given function and
            leaves [trcks.AwaitableSuccessTuple][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> ResultTuple[str, int]:
        ...     if description == "not found":
        ...         return "success", (0,)
        ...     return "failure", description
        ...
        >>> recover_from_not_found = art.map_failure_to_result_iterable(
        ...     _recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure_to_result_iterable(f))


@deprecated("Use map_failure_to_result_iterable instead")
def map_failure_to_result_tuple(
    f: Callable[[_F1], ResultTuple[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_result_iterable][].
    """
    return map_failure_to_result_iterable(f)  # pragma: no cover


@deprecated("Use map_failure_to_iterable instead")
def map_failure_to_tuple(
    f: Callable[[_F1], tuple[_S2, ...]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_failure_to_iterable][].
    """
    return map_failure_to_iterable(f)  # pragma: no cover


def map_successes(
    f: Callable[[_S1], _S2],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map a synchronous function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Function to apply to each success element.

    Returns:
        Function that transforms [trcks.AwaitableSuccessTuple][] values
            element-wise.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> double_integers = art.map_successes(_double_integer)
        >>> a_r_tpl_1 = double_integers(
        ...     art.construct_successes_from_tuple((1, 2, 3))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4, 6))
        >>> a_r_tpl_2 = double_integers(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'not found')
    """
    return a.map_(rt.map_successes(f))


def map_successes_to_awaitable(
    f: Callable[[_S1], Awaitable[_S2]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map an awaitable-returning function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to each success element.

    Returns:
        Function that transforms [trcks.AwaitableSuccessTuple][] values
            element-wise using the given asynchronous function.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_double_integer(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n * 2
        ...
        >>> slowly_double_integers = art.map_successes_to_awaitable(
        ...     _slowly_double_integer
        ... )
        >>> a_r_tpl_1 = slowly_double_integers(
        ...     art.construct_successes_from_tuple((1, 2, 3))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4, 6))
        >>> a_r_tpl_2 = slowly_double_integers(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'not found')
    """
    return map_successes_to_awaitable_result_iterable(
        compose2((f, construct_successes_from_awaitable))
    )


def map_successes_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map a [trcks.AwaitableResult][]-returning function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Asynchronous function to apply to each success element.

    Returns:
        Function that maps over [trcks.AwaitableSuccessTuple][] values and
            returns the first [trcks.AwaitableFailure][] encountered, if any.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_double_integer_if_positive(n: int) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", n * 2
        ...
        >>> slowly_double_integers_if_positive = art.map_successes_to_awaitable_result(
        ...     _slowly_double_integer_if_positive
        ... )
        >>> a_r_tpl_1 = slowly_double_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = slowly_double_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, -1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = slowly_double_integers_if_positive(
        ...     art.construct_failure("oops")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return map_successes_to_awaitable_result_iterable(
        compose2((f, construct_from_awaitable_result))
    )


def map_successes_to_awaitable_result_iterable(
    f: Callable[[_S1], AwaitableResultIterable[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map a [trcks.AwaitableResultIterable][]-returning function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Asynchronous function to apply to each success element.

    Returns:
        Function that flat-maps [trcks.AwaitableSuccessTuple][] values and
            short-circuits on the first [trcks.AwaitableFailure][] returned by `f`.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_duplicate_integer_if_positive(
        ...     n: int,
        ... ) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (n, n)
        ...
        >>> slowly_duplicate_integers_if_positive = (
        ...     art.map_successes_to_awaitable_result_iterable(
        ...         _slowly_duplicate_integer_if_positive
        ...     )
        ... )
        >>> a_r_tpl_1 = slowly_duplicate_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = slowly_duplicate_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, -1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = slowly_duplicate_integers_if_positive(
        ...     art.construct_failure("oops")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """

    async def partially_mapped_f(
        r_tpl: ResultTuple[_F1, _S1],
    ) -> ResultTuple[_F1 | _F2, _S2]:
        match r_tpl:
            case ("failure", _):
                return r_tpl
            case ("success", s1s):
                s2s: list[_S2] = []
                for s1 in s1s:  # pyrefly: ignore[not-iterable]
                    match await f(s1):
                        case ("failure", _) as output_r_tpl:
                            return output_r_tpl
                        case ("success", additional_s2s):
                            s2s.extend(additional_s2s)  # pyrefly: ignore[bad-argument-type]
                        case _ as output_r_tpl:  # pragma: no cover
                            raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                                output_r_tpl, "ResultIterable"
                            )
                return "success", tuple(s2s)
            case _:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_tpl, "ResultTuple"
                )

    return a.map_to_awaitable(partially_mapped_f)


@deprecated("Use map_successes_to_awaitable_result_iterable instead")
def map_successes_to_awaitable_result_tuple(
    f: Callable[[_S1], AwaitableResultTuple[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_awaitable_result_iterable][].
    """
    return map_successes_to_awaitable_result_iterable(f)  # pragma: no cover


def map_successes_to_iterable(
    f: Callable[[_S1], Iterable[_S2]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map a [collections.abc.Iterable][]-returning function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Synchronous function to apply to each success element.

    Returns:
        Function that flat-maps over [trcks.AwaitableSuccessTuple][] values.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _duplicate_integer(n: int) -> tuple[int, int]:
        ...     return n, n
        ...
        >>> duplicate_integers = art.map_successes_to_iterable(_duplicate_integer)
        >>> a_r_tpl = duplicate_integers(art.construct_successes_from_tuple((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 1, 2, 2))
    """
    return a.map_(rt.map_successes_to_iterable(f))


def map_successes_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map a result-returning function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Synchronous function to apply to each success element.

    Returns:
        Function that maps over [trcks.AwaitableSuccessTuple][] values and
            returns the first [trcks.AwaitableFailure][] encountered, if any.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _double_integer_if_positive(n: int) -> Result[str, int]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", n * 2
        ...
        >>> double_integers_if_positive = art.map_successes_to_result(
        ...     _double_integer_if_positive
        ... )
        >>> a_r_tpl_1 = double_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = double_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, -1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = double_integers_if_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return a.map_(rt.map_successes_to_result(f))


def map_successes_to_result_iterable(
    f: Callable[[_S1], ResultIterable[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map a [trcks.ResultIterable][]-returning function over each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Synchronous function to apply to each success element.

    Returns:
        Function that flat-maps [trcks.AwaitableSuccessTuple][] values and
            short-circuits on the first [trcks.AwaitableFailure][] returned by `f`.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _duplicate_integer_if_positive(n: int) -> ResultTuple[str, int]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (n, n)
        ...
        >>> duplicate_integers_if_positive = art.map_successes_to_result_iterable(
        ...     _duplicate_integer_if_positive
        ... )
        >>> a_r_tpl_1 = duplicate_integers_if_positive(
        ...     art.construct_successes_from_tuple((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = duplicate_integers_if_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return a.map_(rt.map_successes_to_result_iterable(f))


@deprecated("Use map_successes_to_result_iterable instead")
def map_successes_to_result_tuple(
    f: Callable[[_S1], ResultTuple[_F2, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_result_iterable][].
    """
    return map_successes_to_result_iterable(f)  # pragma: no cover


@deprecated("Use map_successes_to_iterable instead")
def map_successes_to_tuple(
    f: Callable[[_S1], tuple[_S2, ...]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.map_successes_to_iterable][].
    """
    return map_successes_to_iterable(f)  # pragma: no cover


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply a synchronous side effect to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            returns the original [trcks.AwaitableFailure][] value.
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_failure(description: str) -> None:
        ...     print(f"Failure: {description}")
        ...
        >>> log_failure = art.tap_failure(_log_failure)
        >>> a_r_tpl_1 = log_failure(art.construct_failure("oops"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: oops
        >>> r_tpl_1
        ('failure', 'oops')
        >>> a_r_tpl_2 = log_failure(art.construct_successes_from_tuple((1,)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """
    return a.map_(rt.tap_failure(f))


def tap_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[object]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply an asynchronous side effect to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            returns the original [trcks.AwaitableFailure][] value.
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_log_failure(e: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Failure: {e}")
        ...
        >>> slowly_log_failure = art.tap_failure_to_awaitable(_slowly_log_failure)
        >>> a_r_tpl_1 = slowly_log_failure(art.construct_failure("oops"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: oops
        >>> r_tpl_1
        ('failure', 'oops')
        >>> a_r_tpl_2 = slowly_log_failure(art.construct_successes_from_tuple((1,)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """

    async def bypassed_f(value: _F1) -> _F1:
        _ = await f(value)
        return value

    return map_failure_to_awaitable(bypassed_f)


def tap_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[object, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply an asynchronous side effect with return type [trcks.Result][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.AwaitableSuccess][],
            *this* [trcks.AwaitableSuccess][] is returned (wrapped as a tuple).
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", 0
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = art.tap_failure_to_awaitable_result(
        ...     _slowly_recover_from_not_found
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
    """

    async def bypassed_f(value: _F1) -> ResultTuple[_F1, _S2]:
        match await f(value):
            case ("failure", _):
                return r.construct_failure(value)
            case ("success", s2):
                return rt.construct_successes(s2)  # pyrefly: ignore[bad-return]
            case _ as rslt:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    rslt, "ResultTuple"
                )

    return map_failure_to_awaitable_result_iterable(bypassed_f)


def tap_failure_to_awaitable_result_iterable(
    f: Callable[[_F1], AwaitableResultIterable[object, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply an asynchronous side effect with return type
    [trcks.ResultIterable][] to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.AwaitableSuccessIterable][],
            *this* [trcks.AwaitableSuccessIterable][] is returned
            as a [trcks.AwaitableSuccessTuple][].
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0,)
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = (
        ...     art.tap_failure_to_awaitable_result_iterable(
        ...         _slowly_recover_from_not_found,
        ...     )
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
    """

    async def bypassed_f(value: _F1) -> ResultIterable[_F1, _S2]:
        match await f(value):
            case ("failure", _):
                return r.construct_failure(value)
            case ("success", _) as r_it:
                return r_it
            case _ as r_it:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_it, "ResultIterable"
                )

    return map_failure_to_awaitable_result_iterable(bypassed_f)


@deprecated("Use tap_failure_to_awaitable_result_iterable instead")
def tap_failure_to_awaitable_result_tuple(
    f: Callable[[_F1], AwaitableResultTuple[object, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_awaitable_result_iterable][].
    """
    return tap_failure_to_awaitable_result_iterable(f)  # pragma: no cover


def tap_failure_to_iterable(
    f: Callable[[_F1], Iterable[object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Apply a [collections.abc.Iterable][]-returning side effect
    to [trcks.AwaitableFailure][] values.

    The number of side effect outputs determines how many times the original
    failure value is repeated. The failure is converted to a
    [trcks.AwaitableSuccessTuple][].

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            converts them to [trcks.AwaitableSuccessTuple][] values containing
            the original failure repeated once per element in the
            [collections.abc.Iterable][] returned by the side effect.
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_and_alert(description: str) -> tuple[None, None]:
        ...     return (
        ...         print(f"Failure: {description}"),
        ...         print(f"Logged: {description}"),
        ...     )
        ...
        >>> log_and_alert = art.tap_failure_to_iterable(_log_and_alert)
        >>> a_r_tpl_1 = log_and_alert(art.construct_failure("critical"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: critical
        Logged: critical
        >>> r_tpl_1
        ('success', ('critical', 'critical'))
        >>> a_r_tpl_2 = log_and_alert(art.construct_successes_from_tuple((1,)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """
    return a.map_(rt.tap_failure_to_iterable(f))


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply a synchronous side effect with return type [trcks.Result][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned (wrapped as a tuple).
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> Result[None, int]:
        ...     if description == "not found":
        ...         return "success", 0
        ...     return "failure", None
        ...
        >>> recover_from_not_found = art.tap_failure_to_result(_recover_from_not_found)
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_tuple((1,))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1,))
    """
    return a.map_(rt.tap_failure_to_result(f))


def tap_failure_to_result_iterable(
    f: Callable[[_F1], ResultIterable[object, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply a synchronous side effect with return type [trcks.ResultIterable][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessTuple][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *this* [trcks.SuccessIterable][] is returned
            as a [trcks.SuccessTuple][].
            Passes on [trcks.AwaitableSuccessTuple][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> ResultTuple[None, int]:
        ...     if description == "not found":
        ...         return "success", (0,)
        ...     return "failure", None
        ...
        >>> recover_from_not_found = art.tap_failure_to_result_iterable(
        ...     _recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_tuple((1,))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1,))
    """
    return a.map_(rt.tap_failure_to_result_iterable(f))


@deprecated("Use tap_failure_to_result_iterable instead")
def tap_failure_to_result_tuple(
    f: Callable[[_F1], ResultTuple[object, _S2]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_result_iterable][].
    """
    return tap_failure_to_result_iterable(f)  # pragma: no cover


@deprecated("Use tap_failure_to_iterable instead")
def tap_failure_to_tuple(
    f: Callable[[_F1], tuple[object, ...]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_failure_to_iterable][].
    """
    return tap_failure_to_iterable(f)  # pragma: no cover


def tap_successes(
    f: Callable[[_S1], object],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply a synchronous side effect to each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect and returns the original
            [trcks.AwaitableResultTuple][] value.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_value(n: int) -> None:
        ...     print(f"Value: {n}")
        ...
        >>> log_values = art.tap_successes(_log_value)
        >>> a_r_tpl_1 = log_values(art.construct_successes_from_tuple((1, 2)))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Value: 1
        Value: 2
        >>> r_tpl_1
        ('success', (1, 2))
        >>> a_r_tpl_2 = log_values(art.construct_failure("oops"))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('failure', 'oops')
    """
    return a.map_(rt.tap_successes(f))


def tap_successes_to_awaitable(
    f: Callable[[_S1], Awaitable[object]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply an asynchronous side effect to each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect and returns the original
            [trcks.AwaitableResultTuple][] value.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_log_value(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Value: {n}")
        ...
        >>> slowly_log_values = art.tap_successes_to_awaitable(_slowly_log_value)
        >>> a_r_tpl_1 = slowly_log_values(art.construct_successes_from_tuple((1, 2)))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Value: 1
        Value: 2
        >>> r_tpl_1
        ('success', (1, 2))
        >>> a_r_tpl_2 = slowly_log_values(art.construct_failure("oops"))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('failure', 'oops')
    """

    async def bypassed_f(value: _S1) -> _S1:
        _ = await f(value)
        return value

    return map_successes_to_awaitable(bypassed_f)


def tap_successes_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply an asynchronous side effect with return type [trcks.Result][]
    to each element in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *this* [trcks.AwaitableFailure][] is returned.
            If the given side effect returns a [trcks.AwaitableSuccess][],
            *the original* success element is returned.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _validate_positive(n: int) -> Result[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", None
        ...
        >>> validate_positive = art.tap_successes_to_awaitable_result(
        ...     _validate_positive
        ... )
        >>> a_r_tpl_1 = validate_positive(art.construct_successes_from_tuple((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = validate_positive(
        ...     art.construct_successes_from_tuple((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return tap_successes_to_awaitable_result_iterable(
        compose2((f, construct_from_awaitable_result))
    )


def tap_successes_to_awaitable_result_iterable(
    f: Callable[[_S1], AwaitableResultIterable[_F2, object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply an asynchronous side effect with return type
    [trcks.ResultIterable][] to each element
    in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *this* [trcks.AwaitableFailure][] is returned.
            If the given side effect returns a [trcks.AwaitableSuccessIterable][],
            *the original* success element is repeated once per element
            in the success iterable.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _validate_positive(n: int) -> ResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (None, None)
        ...
        >>> validate_positive = art.tap_successes_to_awaitable_result_iterable(
        ...     _validate_positive
        ... )
        >>> a_r_tpl_1 = validate_positive(art.construct_successes_from_tuple((7,)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7, 7))
        >>> a_r_tpl_2 = validate_positive(
        ...     art.construct_successes_from_tuple((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """

    async def tapped_f(s1: _S1) -> ResultIterable[_F2, _S1]:
        match await f(s1):
            case ("failure", _) as r_tpl:
                return r_tpl
            case ("success", objs):
                return "success", tuple(s1 for _ in objs)  # pyrefly: ignore[not-iterable]
            case _ as r_tpl:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_tpl, "ResultIterable"
                )

    return map_successes_to_awaitable_result_iterable(tapped_f)


@deprecated("Use tap_successes_to_awaitable_result_iterable instead")
def tap_successes_to_awaitable_result_tuple(
    f: Callable[[_S1], AwaitableResultTuple[_F2, object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_awaitable_result_iterable][].
    """
    return tap_successes_to_awaitable_result_iterable(f)  # pragma: no cover


def tap_successes_to_iterable(
    f: Callable[[_S1], Iterable[object]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply a [collections.abc.Iterable][]-returning side effect to each element
    in a [trcks.AwaitableResultTuple][].

    The number of side effect outputs determines how many times each original
    element is repeated in the resulting tuple.

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect and returns a
            [trcks.AwaitableResultTuple][] where each original success element
            is repeated once per element returned by the side effect.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_twice(n: int) -> tuple[None, None]:
        ...     return print(f"Received: {n}"), print(f"Received: {n}")
        ...
        >>> log_twice = art.tap_successes_to_iterable(_log_twice)
        >>> a_r_tpl = log_twice(art.construct_successes_from_tuple((7,)))
        >>> r_tpl = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Received: 7
        Received: 7
        >>> r_tpl
        ('success', (7, 7))
    """
    return a.map_(rt.tap_successes_to_iterable(f))


def tap_successes_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply a synchronous side effect with return type [trcks.Result][]
    to each element in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* success element is returned.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _validate_positive(n: int) -> Result[str, None]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", None
        ...
        >>> validate_positive = art.tap_successes_to_result(_validate_positive)
        >>> a_r_tpl_1 = validate_positive(art.construct_successes_from_tuple((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = validate_positive(
        ...     art.construct_successes_from_tuple((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return a.map_(rt.tap_successes_to_result(f))


def tap_successes_to_result_iterable(
    f: Callable[[_S1], ResultIterable[_F2, object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply a synchronous side effect with return type [trcks.ResultIterable][]
    to each element in a [trcks.AwaitableResultTuple][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* success element is repeated once per element
            in the success iterable.

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _validate_positive_twice(n: int) -> ResultTuple[str, None]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (None, None)
        ...
        >>> validate_positive_twice = art.tap_successes_to_result_iterable(
        ...     _validate_positive_twice
        ... )
        >>> a_r_tpl_1 = validate_positive_twice(
        ...     art.construct_successes_from_tuple((7,))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7, 7))
        >>> a_r_tpl_2 = validate_positive_twice(
        ...     art.construct_successes_from_tuple((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive_twice(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return a.map_(rt.tap_successes_to_result_iterable(f))


@deprecated("Use tap_successes_to_result_iterable instead")
def tap_successes_to_result_tuple(
    f: Callable[[_S1], ResultTuple[_F2, object]],
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_result_iterable][].
    """
    return tap_successes_to_result_iterable(f)  # pragma: no cover


@deprecated("Use tap_successes_to_iterable instead")
def tap_successes_to_tuple(
    f: Callable[[_S1], tuple[object, ...]],
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Deprecated alias for
    [trcks.fp.monads.awaitable_result_tuple.tap_successes_to_iterable][].
    """
    return tap_successes_to_iterable(f)  # pragma: no cover


async def to_coroutine_result_tuple(
    a_r_tpl: AwaitableResultTuple[_F, _S],
) -> ResultTuple[_F, _S]:
    """Turn a [trcks.AwaitableResultTuple][] into a [collections.abc.Coroutine][].

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        a_r_tpl: The [trcks.AwaitableResultTuple][] to be transformed
            into a [collections.abc.Coroutine][].

    Returns:
        The given [trcks.AwaitableResultTuple][] transformed
            into a [collections.abc.Coroutine][].

    Example:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> loop = asyncio.new_event_loop()
        >>> asyncio.set_event_loop(loop)
        >>> future = asyncio.Future[ResultTuple[str, int]]()
        >>> future.set_result(("success", (1, 2)))
        >>> future
        <Future finished result=('success', (1, 2))>
        >>> coro = art.to_coroutine_result_tuple(future)
        >>> coro
        <coroutine object to_coroutine_result_tuple at 0x...>
        >>> asyncio.run(coro)
        ('success', (1, 2))
        >>> loop.close()
    """
    return await a_r_tpl
