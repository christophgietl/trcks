"""Monadic functions for [trcks.AwaitableResultSequence][].

Provides utilities for functional composition of
asynchronous [trcks.ResultSequence][]-returning functions.

Example:
    Map and tap each element inside an awaitable success sequence:

    >>> import asyncio
    >>> from trcks import Result
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_result_sequence as ars
    >>> async def slowly_read_from_disk() -> Result[str, int]:
    ...     await asyncio.sleep(0.001)
    ...     return "success", 3
    ...
    >>> def double_integer(x: int) -> int:
    ...     return x * 2
    ...
    >>> def log_integer(x: int) -> None:
    ...     print(f"Received: {x}")
    ...
    >>> def duplicate_integer(x: int) -> list[int]:
    ...     return [x, x]
    ...
    >>> async def main() -> Result[str, list[int]]:
    ...     return await pipe(
    ...         (
    ...             ars.construct_from_awaitable_result(slowly_read_from_disk()),
    ...             ars.map_successes(double_integer),
    ...             ars.tap_successes(log_integer),
    ...             ars.map_successes_to_sequence(duplicate_integer),
    ...         )
    ...     )
    ...
    >>> result_sequence = asyncio.run(main())
    Received: 6
    >>> result_sequence
    ('success', [6, 6])
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, assert_never
from trcks.fp.composition import compose2
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import result as r
from trcks.fp.monads import result_sequence as rs

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable, Sequence

    from trcks import (
        AwaitableFailure,
        AwaitableResult,
        AwaitableResultSequence,
        AwaitableSuccessSequence,
        Result,
        ResultSequence,
        SuccessSequence,
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
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> a_r_seq = ars.construct_failure("not found")
        >>> isinstance(a_r_seq, Awaitable)
        True
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq))
        ('failure', 'not found')
    """
    return a.construct(rs.construct_failure(value))


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
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> awtbl = a.construct("not found")
        >>> a_r_seq = ars.construct_failure_from_awaitable(awtbl)
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq))
        ('failure', 'not found')
    """
    return a.map_(rs.construct_failure)(awtbl)


def construct_from_awaitable_result(
    a_rslt: AwaitableResult[_F, _S],
) -> AwaitableResultSequence[_F, _S]:
    """Create a [trcks.AwaitableResultSequence][] object
    from a [trcks.AwaitableResult][] object.

    The success payload is wrapped in a single-element sequence.

    Args:
        a_rslt: [trcks.AwaitableResult][] object to be converted.

    Returns:
        A new [trcks.AwaitableResultSequence][] instance where
            the success payload is wrapped in a single-element sequence,
            or the original failure is preserved.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> a_rslt_1 = ar.construct_success(7)
        >>> a_r_seq_1 = ars.construct_from_awaitable_result(a_rslt_1)
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_1))
        ('success', [7])
        >>> a_rslt_2 = ar.construct_failure("oops")
        >>> a_r_seq_2 = ars.construct_from_awaitable_result(a_rslt_2)
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_2))
        ('failure', 'oops')
    """
    return a.map_(rs.construct_from_result)(a_rslt)


def construct_from_result(rslt: Result[_F, _S]) -> AwaitableResultSequence[_F, _S]:
    """Create a [trcks.AwaitableResultSequence][] object from a [trcks.Result][].

    The success payload is wrapped in a single-element sequence.

    Args:
        rslt: [trcks.Result][] object to be converted.

    Returns:
        A new [trcks.AwaitableResultSequence][] instance where
            the success payload is wrapped in a single-element sequence,
            or the original failure is preserved.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> a_r_seq_1 = ars.construct_from_result(("success", 7))
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_1))
        ('success', [7])
        >>> a_r_seq_2 = ars.construct_from_result(("failure", "oops"))
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_2))
        ('failure', 'oops')
    """
    return a.construct(rs.construct_from_result(rslt))


def construct_from_result_sequence(
    r_seq: ResultSequence[_F, _S],
) -> AwaitableResultSequence[_F, _S]:
    """Create a [trcks.AwaitableResultSequence][] object
    from a [trcks.ResultSequence][] object.

    Args:
        r_seq: [trcks.ResultSequence][] object to be wrapped
            in an [trcks.AwaitableResultSequence][] object.

    Returns:
        A new [trcks.AwaitableResultSequence][] instance containing
            the given [trcks.ResultSequence][] object.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> a_r_seq = ars.construct_from_result_sequence(("success", [1, 2]))
        >>> isinstance(a_r_seq, Awaitable)
        True
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq))
        ('success', [1, 2])
    """
    return a.construct(r_seq)


def construct_successes(value: _S) -> AwaitableSuccessSequence[_S]:
    """Create a [trcks.AwaitableSuccessSequence][] object from a single value.

    Args:
        value: A single value.

    Returns:
        A new [trcks.AwaitableSuccessSequence][] instance containing
            the single value in a sequence.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> a_r_seq = ars.construct_successes(42)
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq))
        ('success', [42])
    """
    return a.construct(rs.construct_successes(value))


def construct_successes_from_awaitable(
    awtbl: Awaitable[_S],
) -> AwaitableSuccessSequence[_S]:
    """Create a [trcks.AwaitableSuccessSequence][] object
    from a [collections.abc.Awaitable][] object.

    The value of the awaitable is wrapped in a single-element success sequence.

    Args:
        awtbl: [collections.abc.Awaitable][] object whose resolved value
            will be wrapped in a [trcks.AwaitableSuccessSequence][].

    Returns:
        A new [trcks.AwaitableSuccessSequence][] instance containing
            the value of the given [collections.abc.Awaitable][] in a sequence.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> awtbl = a.construct(7)
        >>> a_r_seq = ars.construct_successes_from_awaitable(awtbl)
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq))
        ('success', [7])
    """
    return a.map_(rs.construct_successes)(awtbl)


def construct_successes_from_sequence(
    seq: Sequence[_S],
) -> AwaitableSuccessSequence[_S]:
    """Create a [trcks.AwaitableSuccessSequence][] object from a sequence.

    Args:
        seq: Sequence to be wrapped in a [trcks.AwaitableSuccessSequence][].

    Returns:
        A new [trcks.AwaitableSuccessSequence][] instance containing
            the given sequence.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> a_r_seq = ars.construct_successes_from_sequence([1, 2])
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq))
        ('success', [1, 2])
    """
    return a.construct(rs.construct_successes_from_sequence(seq))


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F2, _S1]]:
    """Create function that maps [trcks.AwaitableFailure][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableFailure][] values
            according to the given function and
            leaves [trcks.AwaitableSuccessSequence][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _add_prefix(description: str) -> str:
        ...     return f"err: {description}"
        ...
        >>> add_prefix = ars.map_failure(_add_prefix)
        >>> a_r_seq_1 = add_prefix(ars.construct_failure("not found"))
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_1))
        ('failure', 'err: not found')
        >>> a_r_seq_2 = add_prefix(ars.construct_successes_from_sequence([1, 2]))
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_2))
        ('success', [1, 2])
    """
    return a.map_(rs.map_failure(f))


def map_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[_F2]],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F2, _S1]]:
    """Create function that maps [trcks.AwaitableFailure][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableFailure][] values
            according to the given asynchronous function and
            leaves [trcks.AwaitableSuccessSequence][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_add_prefix(s: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"err: {s}"
        ...
        >>> slowly_add_prefix = ars.map_failure_to_awaitable(_slowly_add_prefix)
        >>> a_r_seq_1 = slowly_add_prefix(ars.construct_failure("not found"))
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_1))
        ('failure', 'err: not found')
        >>> a_r_seq_2 = slowly_add_prefix(
        ...     ars.construct_successes_from_sequence([1, 2])
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_2))
        ('success', [1, 2])
    """
    return map_failure_to_awaitable_result_sequence(
        compose2((f, construct_failure_from_awaitable))
    )


def map_failure_to_awaitable_result_sequence(
    f: Callable[[_F1], AwaitableResultSequence[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F2, _S1 | _S2],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResultSequence][] values.

    [trcks.AwaitableSuccessSequence][] values are left unchanged.

    Args:
        f: Asynchronous function that transforms a failure into
            a new [trcks.AwaitableResultSequence][].

    Returns:
        Maps [trcks.AwaitableFailure][] values to new
            [trcks.AwaitableResultSequence][] values
            according to the given asynchronous function and
            leaves [trcks.AwaitableSuccessSequence][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_recover(e: str) -> ResultSequence[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", [0]
        ...     return "failure", e
        ...
        >>> slowly_recover = ars.map_failure_to_awaitable_result_sequence(
        ...     _slowly_recover
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        ('success', [1, 2])
    """

    async def partially_mapped_f(
        rslt_seq: ResultSequence[_F1, _S1],
    ) -> ResultSequence[_F2, _S1 | _S2]:
        match rslt_seq[0]:
            case "failure":
                return await f(rslt_seq[1])
            case "success":
                return rslt_seq
            case _:  # pragma: no cover
                return assert_never(rslt_seq)  # type: ignore [unreachable]  # pyright: ignore [reportUnreachable]

    return a.map_to_awaitable(partially_mapped_f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F2, _S1 | _S2],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResultSequence][] values.

    [trcks.AwaitableSuccessSequence][] values are left unchanged.

    Args:
        f: Synchronous function that transforms a failure into
            a new [trcks.Result][].

    Returns:
        Maps [trcks.AwaitableFailure][] values to new
            [trcks.AwaitableResultSequence][] values
            according to the given function and
            leaves [trcks.AwaitableSuccessSequence][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _recover_from_not_found(description: str) -> Result[str, int]:
        ...     if description == "not found":
        ...         return ("success", 0)
        ...     return ("failure", description)
        ...
        >>> recover_from_not_found = ars.map_failure_to_result(_recover_from_not_found)
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        ('success', [1, 2])
    """
    return a.map_(rs.map_failure_to_result(f))


def map_failure_to_result_sequence(
    f: Callable[[_F1], ResultSequence[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F2, _S1 | _S2],
]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResultSequence][] values.

    [trcks.AwaitableSuccessSequence][] values are left unchanged.

    Args:
        f: Synchronous function that transforms a failure into
            a new [trcks.ResultSequence][].

    Returns:
        Maps [trcks.AwaitableFailure][] values to new
            [trcks.AwaitableResultSequence][] values
            according to the given function and
            leaves [trcks.AwaitableSuccessSequence][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _recover_from_not_found(description: str) -> ResultSequence[str, int]:
        ...     if description == "not found":
        ...         return ("success", [0])
        ...     return ("failure", description)
        ...
        >>> recover_from_not_found = ars.map_failure_to_result_sequence(
        ...     _recover_from_not_found
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        ('success', [1, 2])
    """
    return a.map_(rs.map_failure_to_result_sequence(f))


def map_failure_to_sequence(
    f: Callable[[_F1], Sequence[_S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    Awaitable[SuccessSequence[_S1] | SuccessSequence[_S2]],
]:
    """Create function that maps [trcks.AwaitableFailure][] values to sequences.

    [trcks.AwaitableSuccessSequence][] values are left unchanged.

    Args:
        f: Synchronous function that transforms a failure into a sequence.

    Returns:
        Maps [trcks.AwaitableFailure][] values to sequences wrapped in
            [trcks.AwaitableSuccessSequence][] values and
            leaves [trcks.AwaitableSuccessSequence][] values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _recover(description: str) -> list[int]:
        ...     if description == "not found":
        ...         return [0]
        ...     return []
        ...
        >>> recover = ars.map_failure_to_sequence(_recover)
        >>> asyncio.run(recover(ars.construct_failure("not found")))
        ('success', [0])
        >>> asyncio.run(recover(ars.construct_failure("fatal")))
        ('success', [])
        >>> asyncio.run(recover(ars.construct_successes_from_sequence([1, 2])))
        ('success', [1, 2])
    """
    return a.map_(rs.map_failure_to_sequence(f))


def map_successes(
    f: Callable[[_S1], _S2],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S2]]:
    """Map a synchronous function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Function to apply to each success element.

    Returns:
        Function that transforms [trcks.AwaitableSuccessSequence][] values
            element-wise.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> double_integers = ars.map_successes(_double_integer)
        >>> a_r_seq_1 = double_integers(
        ...     ars.construct_successes_from_sequence([1, 2, 3])
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_1))
        ('success', [2, 4, 6])
        >>> a_r_seq_2 = double_integers(ars.construct_failure("not found"))
        >>> asyncio.run(ars.to_coroutine_result_sequence(a_r_seq_2))
        ('failure', 'not found')
    """
    return a.map_(rs.map_successes(f))


def map_successes_to_awaitable(
    f: Callable[[_S1], Awaitable[_S2]],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S2]]:
    """Map an awaitable-returning function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to each success element.

    Returns:
        Function that transforms [trcks.AwaitableSuccessSequence][] values
            element-wise using the given asynchronous function.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_double_integer(x: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return x * 2
        ...
        >>> slowly_double_integers = ars.map_successes_to_awaitable(
        ...     _slowly_double_integer
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_double_integers(ars.construct_successes_from_sequence([1, 2, 3]))
        ... ))
        ('success', [2, 4, 6])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_double_integers(ars.construct_failure("not found"))
        ... ))
        ('failure', 'not found')
    """
    return map_successes_to_awaitable_result_sequence(
        compose2((f, construct_successes_from_awaitable))
    )


def map_successes_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S2],
]:
    """Map an [trcks.AwaitableResult][]-returning function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Asynchronous function returning an [trcks.AwaitableResult][]
            for each success element.

    Returns:
        Function that maps over [trcks.AwaitableSuccessSequence][] values and
            returns the first [trcks.AwaitableFailure][] encountered, if any.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_double_integer_if_positive(x: int) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if x <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", x * 2)
        ...
        >>> slowly_double_integers_if_positive = ars.map_successes_to_awaitable_result(
        ...     _slowly_double_integer_if_positive
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_double_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, 2])
        ...     )
        ... ))
        ('success', [2, 4])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_double_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, -1, 2])
        ...     )
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_double_integers_if_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """
    return map_successes_to_awaitable_result_sequence(
        compose2((f, construct_from_awaitable_result))
    )


def map_successes_to_awaitable_result_sequence(
    f: Callable[[_S1], AwaitableResultSequence[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S2],
]:
    """Map an [trcks.AwaitableResultSequence][]-returning function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Asynchronous function returning an [trcks.AwaitableResultSequence][]
            for each success element.

    Returns:
        Function that flat-maps [trcks.AwaitableSuccessSequence][] values and
            short-circuits on the first [trcks.AwaitableFailure][] returned by `f`.

    Example:
        >>> import asyncio
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_duplicate_integer_if_positive(
        ...     x: int,
        ... ) -> ResultSequence[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if x <= 0:
        ...         return "failure", "bad"
        ...     return "success", [x, x]
        ...
        >>> slowly_duplicate_integers_if_positive = (
        ...     ars.map_successes_to_awaitable_result_sequence(
        ...         _slowly_duplicate_integer_if_positive
        ...     )
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_duplicate_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, 2])
        ...     )
        ... ))
        ('success', [1, 1, 2, 2])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_duplicate_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, -1, 2])
        ...     )
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_duplicate_integers_if_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """

    async def partially_mapped_f(
        rslt_seq: ResultSequence[_F1, _S1],
    ) -> ResultSequence[_F1 | _F2, _S2]:
        match rslt_seq[0]:
            case "failure":
                return rslt_seq
            case "success":
                s2s: list[_S2] = []
                for s1 in rslt_seq[1]:
                    inner = await f(s1)
                    match inner[0]:
                        case "failure":
                            return inner
                        case "success":
                            s2s.extend(inner[1])
                        case _:  # pragma: no cover
                            return assert_never(inner)  # type: ignore [unreachable]  # pyright: ignore [reportUnreachable]
                return "success", s2s
            case _:  # pragma: no cover
                return assert_never(rslt_seq)  # type: ignore [unreachable]  # pyright: ignore [reportUnreachable]

    return a.map_to_awaitable(partially_mapped_f)


def map_successes_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S2],
]:
    """Map a result-returning function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Synchronous function returning a [trcks.Result][]
            for each success element.

    Returns:
        Function that maps over [trcks.AwaitableSuccessSequence][] values and
            returns the first [trcks.AwaitableFailure][] encountered, if any.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _double_integer_if_positive(n: int) -> Result[str, int]:
        ...     if n <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", n * 2)
        ...
        >>> double_integers_if_positive = ars.map_successes_to_result(
        ...     _double_integer_if_positive
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     double_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, 2])
        ...     )
        ... ))
        ('success', [2, 4])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     double_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, -1, 2])
        ...     )
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     double_integers_if_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """
    return a.map_(rs.map_successes_to_result(f))


def map_successes_to_result_sequence(
    f: Callable[[_S1], ResultSequence[_F2, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S2],
]:
    """Map a sequence-returning result function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.
    Short-circuits on the first failure returned by `f`.

    Args:
        f: Synchronous function returning a [trcks.ResultSequence][]
            for each success element.

    Returns:
        Function that flat-maps [trcks.AwaitableSuccessSequence][] values and
            short-circuits on the first [trcks.AwaitableFailure][] returned by `f`.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _duplicate_integer_if_positive(n: int) -> ResultSequence[str, int]:
        ...     if n <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", [n, n])
        ...
        >>> duplicate_integers_if_positive = ars.map_successes_to_result_sequence(
        ...     _duplicate_integer_if_positive
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     duplicate_integers_if_positive(
        ...         ars.construct_successes_from_sequence([1, 2])
        ...     )
        ... ))
        ('success', [1, 1, 2, 2])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     duplicate_integers_if_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """
    return a.map_(rs.map_successes_to_result_sequence(f))


def map_successes_to_sequence(
    f: Callable[[_S1], Sequence[_S2]],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S2]]:
    """Map a sequence-returning function over each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Synchronous function returning a sequence for each success element.

    Returns:
        Function that flat-maps over [trcks.AwaitableSuccessSequence][] values.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _duplicate_integer(n: int) -> list[int]:
        ...     return [n, n]
        ...
        >>> duplicate_integers = ars.map_successes_to_sequence(_duplicate_integer)
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     duplicate_integers(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        ('success', [1, 1, 2, 2])
    """
    return a.map_(rs.map_successes_to_sequence(f))


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S1]]:
    """Apply a synchronous side effect to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            returns the original [trcks.AwaitableFailure][] value.
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _log_failure(description: str) -> None:
        ...     print(f"Failure: {description}")
        ...
        >>> log_failure = ars.tap_failure(_log_failure)
        >>> result_sequence_1 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     log_failure(ars.construct_failure("oops"))
        ... ))
        Failure: oops
        >>> result_sequence_1
        ('failure', 'oops')
        >>> result_sequence_2 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     log_failure(ars.construct_successes_from_sequence([1]))
        ... ))
        >>> result_sequence_2
        ('success', [1])
    """
    return a.map_(rs.tap_failure(f))


def tap_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[object]],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S1]]:
    """Apply an asynchronous side effect to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            returns the original [trcks.AwaitableFailure][] value.
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_log_failure(e: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Failure: {e}")
        ...
        >>> slowly_log_failure = ars.tap_failure_to_awaitable(_slowly_log_failure)
        >>> result_sequence_1 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_log_failure(ars.construct_failure("oops"))
        ... ))
        Failure: oops
        >>> result_sequence_1
        ('failure', 'oops')
        >>> result_sequence_2 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_log_failure(ars.construct_successes_from_sequence([1]))
        ... ))
        >>> result_sequence_2
        ('success', [1])
    """

    async def bypassed_f(value: _F1) -> _F1:
        _ = await f(value)
        return value

    return map_failure_to_awaitable(bypassed_f)


def tap_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[object, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1, _S1 | _S2],
]:
    """Apply an asynchronous side effect with return type [trcks.AwaitableResult][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.AwaitableSuccess][],
            *this* [trcks.AwaitableSuccess][] is returned (wrapped as a sequence).
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_recover(e: str) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return ("success", 0)
        ...     return ("failure", e)
        ...
        >>> slowly_recover = ars.tap_failure_to_awaitable_result(_slowly_recover)
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
    """

    async def bypassed_f(value: _F1) -> ResultSequence[_F1, _S2]:
        rslt: Result[object, _S2] = await f(value)
        match rslt[0]:
            case "failure":
                return r.construct_failure(value)
            case "success":
                return rs.construct_from_result(rslt)
            case _:  # pragma: no cover
                return assert_never(rslt)  # type: ignore [unreachable]  # pyright: ignore [reportUnreachable]

    return map_failure_to_awaitable_result_sequence(bypassed_f)


def tap_failure_to_awaitable_result_sequence(
    f: Callable[[_F1], AwaitableResultSequence[object, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1, _S1 | _S2],
]:
    """Apply an asynchronous side effect with return type
    [trcks.AwaitableResultSequence][] to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.AwaitableSuccessSequence][],
            *this* [trcks.AwaitableSuccessSequence][] is returned.
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_recover(e: str) -> ResultSequence[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return ("success", [0])
        ...     return ("failure", e)
        ...
        >>> slowly_recover = ars.tap_failure_to_awaitable_result_sequence(
        ...     _slowly_recover
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_recover(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
    """

    async def bypassed_f(value: _F1) -> ResultSequence[_F1, _S2]:
        rslt_seq: ResultSequence[object, _S2] = await f(value)
        match rslt_seq[0]:
            case "failure":
                return r.construct_failure(value)
            case "success":
                return rslt_seq
            case _:  # pragma: no cover
                return assert_never(rslt_seq)  # type: ignore [unreachable]  # pyright: ignore [reportUnreachable]

    return map_failure_to_awaitable_result_sequence(bypassed_f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1, _S1 | _S2],
]:
    """Apply a synchronous side effect with return type [trcks.Result][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned (wrapped as a sequence).
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _recover_from_not_found(description: str) -> Result[None, int]:
        ...     if description == "not found":
        ...         return ("success", 0)
        ...     return ("failure", None)
        ...
        >>> recover_from_not_found = ars.tap_failure_to_result(_recover_from_not_found)
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_successes_from_sequence([1]))
        ... ))
        ('success', [1])
    """
    return a.map_(rs.tap_failure_to_result(f))


def tap_failure_to_result_sequence(
    f: Callable[[_F1], ResultSequence[object, _S2]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1, _S1 | _S2],
]:
    """Apply a synchronous side effect with return type [trcks.ResultSequence][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.SuccessSequence][],
            *this* [trcks.SuccessSequence][] is returned.
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _recover_from_not_found(description: str) -> ResultSequence[None, int]:
        ...     if description == "not found":
        ...         return ("success", [0])
        ...     return ("failure", None)
        ...
        >>> recover_from_not_found = ars.tap_failure_to_result_sequence(
        ...     _recover_from_not_found
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("not found"))
        ... ))
        ('success', [0])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_failure("fatal"))
        ... ))
        ('failure', 'fatal')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     recover_from_not_found(ars.construct_successes_from_sequence([1]))
        ... ))
        ('success', [1])
    """
    return a.map_(rs.tap_failure_to_result_sequence(f))


def tap_failure_to_sequence(
    f: Callable[[_F1], Sequence[object]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    Awaitable[SuccessSequence[_F1] | SuccessSequence[_S1]],
]:
    """Apply a sequence-returning side effect to [trcks.AwaitableFailure][] values.

    The number of side-effect outputs determines how many times the original
    failure value is repeated. The failure is converted to an
    [trcks.AwaitableSuccessSequence][].

    [trcks.AwaitableSuccessSequence][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value
            that returns a sequence.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            converts them to [trcks.AwaitableSuccessSequence][] values containing
            the original failure repeated once per element in the sequence returned
            by the side effect.
            Passes on [trcks.AwaitableSuccessSequence][] values without side effects.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _log_and_alert(description: str) -> list[None]:
        ...     return [
        ...         print(f"Failure: {description}"),
        ...         print(f"Logged: {description}"),
        ...     ]
        ...
        >>> log_and_alert = ars.tap_failure_to_sequence(_log_and_alert)
        >>> result_sequence_1 = asyncio.run(
        ...     log_and_alert(ars.construct_failure("critical"))
        ... )
        Failure: critical
        Logged: critical
        >>> result_sequence_1
        ('success', ['critical', 'critical'])
        >>> result_sequence_2 = asyncio.run(
        ...     log_and_alert(ars.construct_successes_from_sequence([1]))
        ... )
        >>> result_sequence_2
        ('success', [1])
    """
    return a.map_(rs.tap_failure_to_sequence(f))


def tap_successes(
    f: Callable[[_S1], object],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S1]]:
    """Apply a synchronous side effect to each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect and returns the original
            [trcks.AwaitableResultSequence][] value.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _log_value(x: int) -> None:
        ...     print(f"Value: {x}")
        ...
        >>> log_values = ars.tap_successes(_log_value)
        >>> result_sequence_1 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     log_values(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        Value: 1
        Value: 2
        >>> result_sequence_1
        ('success', [1, 2])
        >>> result_sequence_2 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     log_values(ars.construct_failure("oops"))
        ... ))
        >>> result_sequence_2
        ('failure', 'oops')
    """
    return a.map_(rs.tap_successes(f))


def tap_successes_to_awaitable(
    f: Callable[[_S1], Awaitable[object]],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S1]]:
    """Apply an asynchronous side effect to each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect and returns the original
            [trcks.AwaitableResultSequence][] value.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _slowly_log_value(x: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Value: {x}")
        ...
        >>> slowly_log_values = ars.tap_successes_to_awaitable(_slowly_log_value)
        >>> result_sequence_1 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_log_values(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        Value: 1
        Value: 2
        >>> result_sequence_1
        ('success', [1, 2])
        >>> result_sequence_2 = asyncio.run(ars.to_coroutine_result_sequence(
        ...     slowly_log_values(ars.construct_failure("oops"))
        ... ))
        >>> result_sequence_2
        ('failure', 'oops')
    """

    async def bypassed_f(value: _S1) -> _S1:
        _ = await f(value)
        return value

    return map_successes_to_awaitable(bypassed_f)


def tap_successes_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, object]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S1],
]:
    """Apply an asynchronous side effect with return type [trcks.AwaitableResult][]
    to each element in an [trcks.AwaitableResultSequence][].

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
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _validate_positive(x: int) -> Result[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if x <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", None)
        ...
        >>> validate_positive = ars.tap_successes_to_awaitable_result(
        ...     _validate_positive
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        ('success', [1, 2])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_successes_from_sequence([1, -1]))
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """
    return tap_successes_to_awaitable_result_sequence(
        compose2((f, construct_from_awaitable_result))
    )


def tap_successes_to_awaitable_result_sequence(
    f: Callable[[_S1], AwaitableResultSequence[_F2, object]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S1],
]:
    """Apply an asynchronous side effect with return type
    [trcks.AwaitableResultSequence][] to each element
    in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *this* [trcks.AwaitableFailure][] is returned.
            If the given side effect returns an [trcks.AwaitableSuccessSequence][],
            *the original* success element is repeated once per element
            in the side effect output.

    Example:
        >>> import asyncio
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> async def _validate_positive(x: int) -> ResultSequence[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if x <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", [None, None])
        ...
        >>> validate_positive = ars.tap_successes_to_awaitable_result_sequence(
        ...     _validate_positive
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_successes_from_sequence([7]))
        ... ))
        ('success', [7, 7])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_successes_from_sequence([1, -1]))
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """

    async def tapped_f(s1: _S1) -> ResultSequence[_F2, _S1]:
        rslt_seq: ResultSequence[_F2, object] = await f(s1)
        match rslt_seq[0]:
            case "failure":
                return rslt_seq
            case "success":
                return ("success", [s1 for _ in rslt_seq[1]])
            case _:  # pragma: no cover
                return assert_never(rslt_seq)  # type: ignore [unreachable]  # pyright: ignore [reportUnreachable]

    return map_successes_to_awaitable_result_sequence(tapped_f)


def tap_successes_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S1],
]:
    """Apply a synchronous side effect with return type [trcks.Result][]
    to each element in an [trcks.AwaitableResultSequence][].

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
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _validate_positive(n: int) -> Result[str, None]:
        ...     if n <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", None)
        ...
        >>> validate_positive = ars.tap_successes_to_result(_validate_positive)
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_successes_from_sequence([1, 2]))
        ... ))
        ('success', [1, 2])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_successes_from_sequence([1, -1]))
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """
    return a.map_(rs.tap_successes_to_result(f))


def tap_successes_to_result_sequence(
    f: Callable[[_S1], ResultSequence[_F2, object]],
) -> Callable[
    [AwaitableResultSequence[_F1, _S1]],
    AwaitableResultSequence[_F1 | _F2, _S1],
]:
    """Apply a synchronous side effect with return type [trcks.ResultSequence][]
    to each element in an [trcks.AwaitableResultSequence][].

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessSequence][],
            *the original* success element is repeated once per element
            in the side effect output.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _validate_positive_twice(n: int) -> ResultSequence[str, None]:
        ...     if n <= 0:
        ...         return ("failure", "bad")
        ...     return ("success", [None, None])
        ...
        >>> validate_positive_twice = ars.tap_successes_to_result_sequence(
        ...     _validate_positive_twice
        ... )
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive_twice(ars.construct_successes_from_sequence([7]))
        ... ))
        ('success', [7, 7])
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive_twice(ars.construct_successes_from_sequence([1, -1]))
        ... ))
        ('failure', 'bad')
        >>> asyncio.run(ars.to_coroutine_result_sequence(
        ...     validate_positive_twice(ars.construct_failure("oops"))
        ... ))
        ('failure', 'oops')
    """
    return a.map_(rs.tap_successes_to_result_sequence(f))


def tap_successes_to_sequence(
    f: Callable[[_S1], Sequence[object]],
) -> Callable[[AwaitableResultSequence[_F1, _S1]], AwaitableResultSequence[_F1, _S1]]:
    """Apply a sequence-returning side effect to each element
    in an [trcks.AwaitableResultSequence][].

    The number of side-effect outputs determines how many times each original
    element is repeated in the resulting sequence.

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to each success element that
            returns a sequence.

    Returns:
        Applies the given side effect and returns an
            [trcks.AwaitableResultSequence][] where each original success element
            is repeated once per element returned by the side effect.

    Example:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> def _log_twice(n: int) -> list[None]:
        ...     return [print(f"Received: {n}"), print(f"Received: {n}")]
        ...
        >>> log_twice = ars.tap_successes_to_sequence(_log_twice)
        >>> result_sequence = asyncio.run(ars.to_coroutine_result_sequence(
        ...     log_twice(ars.construct_successes_from_sequence([7]))
        ... ))
        Received: 7
        Received: 7
        >>> result_sequence
        ('success', [7, 7])
    """
    return a.map_(rs.tap_successes_to_sequence(f))


async def to_coroutine_result_sequence(
    a_r_seq: AwaitableResultSequence[_F, _S],
) -> ResultSequence[_F, _S]:
    """Turn a [trcks.AwaitableResultSequence][] into a [collections.abc.Coroutine][].

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        a_r_seq: The [trcks.AwaitableResultSequence][] to be transformed
            into a [collections.abc.Coroutine][].

    Returns:
        The given [trcks.AwaitableResultSequence][] transformed
            into a [collections.abc.Coroutine][].

    Example:
        >>> import asyncio
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import awaitable_result_sequence as ars
        >>> asyncio.set_event_loop(asyncio.new_event_loop())
        >>> future = asyncio.Future[ResultSequence[str, int]]()
        >>> future.set_result(("success", [1, 2]))
        >>> future
        <Future finished result=('success', [1, 2])>
        >>> coro = ars.to_coroutine_result_sequence(future)
        >>> coro
        <coroutine object to_coroutine_result_sequence at 0x...>
        >>> asyncio.run(coro)
        ('success', [1, 2])
    """
    return await a_r_seq
