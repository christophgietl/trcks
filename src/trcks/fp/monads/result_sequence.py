"""Monadic functions for [trcks.ResultSequence][].

Provides utilities for functional composition of
functions returning [trcks.ResultSequence][] values.

Example:
    Map and tap each element inside a success sequence:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result_sequence as rs
    >>> def double(n: int) -> int:
    ...     return n * 2
    ...
    >>> def duplicate(n: int) -> list[int]:
    ...     return [n, -n]
    ...
    >>> def log(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> result_sequence = pipe(
    ...     (
    ...         rs.construct_successes_from_sequence([1, 2, 3]),
    ...         rs.map_successes(double),
    ...         rs.tap_successes(log),
    ...         rs.map_successes_to_sequence(duplicate),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> result_sequence
    ('success', [2, -2, 4, -4, 6, -6])
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, assert_never
from trcks.fp.composition import compose2
from trcks.fp.monads import result as r
from trcks.fp.monads import sequence as s

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable, Sequence

    from trcks import Failure, Result, ResultSequence, SuccessSequence

__docformat__ = "google"

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def construct_failure(value: _F) -> Failure[_F]:
    """Create a [trcks.Failure][] object from a value.

    Args:
        value: Value to be wrapped in a [trcks.Failure][].

    Returns:
        [trcks.Failure][] object containing the given value.

    Note:
        This function is an alias for
        [trcks.fp.monads.result.construct_failure][].

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_failure("not found")
        ('failure', 'not found')
    """
    return r.construct_failure(value)


def construct_from_result(rslt: Result[_F, _S]) -> ResultSequence[_F, _S]:
    """Create a [trcks.ResultSequence][] object from a [trcks.Result][].

    Args:
        rslt: The [trcks.Result][] object to be wrapped.

    Returns:
        A new [trcks.ResultSequence][] instance with the success payload
            wrapped in a sequence.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_from_result(("success", 7))
        ('success', [7])
        >>> rs.construct_from_result(("failure", "oops"))
        ('failure', 'oops')
    """
    return r.map_success(s.construct)(rslt)


def construct_successes(value: _S) -> SuccessSequence[_S]:
    """Create a [trcks.SuccessSequence][] object from a single value.

    Args:
        value: A single value.

    Returns:
        A new [trcks.SuccessSequence][] instance containing the single value.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_successes(42)
        ('success', [42])
    """
    return r.construct_success(s.construct(value))


def construct_successes_from_sequence(seq: Sequence[_S]) -> SuccessSequence[_S]:
    """Create a [trcks.SuccessSequence][] object from a sequence.

    Args:
        seq: Sequence to be wrapped in a [trcks.SuccessSequence][].

    Returns:
        A new [trcks.SuccessSequence][] instance containing the given sequence.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_successes_from_sequence([1, 2])
        ('success', [1, 2])
    """
    return r.construct_success(seq)


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F2, _S1]]:
    """Create function that maps [trcks.Failure][] values to [trcks.Failure][] values.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.Failure][] values
            according to the given function and
            leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _add_prefix(e: str) -> str:
        ...     return f"err: {e}"
        ...
        >>> add_prefix: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.map_failure(_add_prefix)
        >>> add_prefix(("failure", "not found"))
        ('failure', 'err: not found')
        >>> add_prefix(("success", [1, 2]))
        ('success', [1, 2])
    """
    return r.map_failure(f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F2, Sequence[_S1] | Sequence[_S2]]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.Failure][] and [trcks.Success][]
            values according to the given function and
            leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks import Result, ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _recover_from_not_found(description: str) -> Result[str, int]:
        ...     if description == "not found":
        ...         return ("success", 0)
        ...     return ("failure", description)
        ...
        >>> recover_from_not_found: Callable[
        ...     [ResultSequence[str, int]], Result[str, Sequence[int]]
        ... ] = rs.map_failure_to_result(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', [0])
        >>> recover_from_not_found(("failure", "not authorized"))
        ('failure', 'not authorized')
        >>> recover_from_not_found(("success", [1, 2]))
        ('success', [1, 2])
    """
    return map_failure_to_result_sequence(compose2((f, construct_from_result)))


def map_failure_to_result_sequence(
    f: Callable[[_F1], ResultSequence[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F2, Sequence[_S1] | Sequence[_S2]]]:
    """Create function that maps [trcks.Failure][] values
    to new [trcks.ResultSequence][] values.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.ResultSequence][] values
            according to the given function and
            leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks import Result, ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _recover_from_not_found(description: str) -> ResultSequence[str, int]:
        ...     if description == "not found":
        ...         return ("success", [0])
        ...     return ("failure", description)
        ...
        >>> recover_from_not_found: Callable[
        ...     [ResultSequence[str, int]], Result[str, Sequence[int]]
        ... ] = rs.map_failure_to_result_sequence(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', [0])
        >>> recover_from_not_found(("failure", "not authorized"))
        ('failure', 'not authorized')
        >>> recover_from_not_found(("success", [1, 2]))
        ('success', [1, 2])
    """
    return r.map_failure_to_result(f)


def map_failure_to_sequence(
    f: Callable[[_F1], Sequence[_S2]],
) -> Callable[[ResultSequence[_F1, _S1]], SuccessSequence[_S1] | SuccessSequence[_S2]]:
    """Create function that maps [trcks.Failure][] values
    to [collections.abc.Sequence][]s.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to [collections.abc.Sequence][]s wrapped
            in a [trcks.Success][] according to the given function and
            leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence, SuccessSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _recover_from_not_found(description: str) -> list[int]:
        ...     if description == "not found":
        ...         return [0]
        ...     return []
        ...
        >>> recover_from_not_found: Callable[
        ...     [ResultSequence[str, int]], SuccessSequence[int]
        ... ] = rs.map_failure_to_sequence(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', [0])
        >>> recover_from_not_found(("failure", "not authorized"))
        ('success', [])
        >>> recover_from_not_found(("success", [1, 2]))
        ('success', [1, 2])
    """

    def mapped_f(
        rs: ResultSequence[_F1, _S1],
    ) -> SuccessSequence[_S1] | SuccessSequence[_S2]:
        match rs[0]:
            case "failure":
                return "success", f(rs[1])
            case "success":
                return rs
            case _:  # pragma: no cover
                return assert_never(rs[0])  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]

    return mapped_f


def map_successes(
    f: Callable[[_S1], _S2],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S2]]:
    """Create function that maps each element of a [trcks.SuccessSequence][]
    to a new element.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps each element of a [trcks.SuccessSequence][] to a new element
            according to the given function.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _double(n: int) -> int:
        ...     return n * 2
        ...
        >>> double: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.map_successes(_double)
        >>> double(("success", [1, 2, 3]))
        ('success', [2, 4, 6])
        >>> double(("failure", "not found"))
        ('failure', 'not found')
    """
    return r.map_success(s.map_(f))


def map_successes_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S2]]:
    """Create function that maps each element of a [trcks.SuccessSequence][]
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps each element of a [trcks.SuccessSequence][] to
            [trcks.Failure][] and [trcks.Success][] values according to the given
            function, returning the first [trcks.Failure][] encountered, if any.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import Result, ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _double_if_positive(n: int) -> Result[str, int]:
        ...     if n > 0:
        ...         return ("success", n * 2)
        ...     return ("failure", "bad")
        ...
        >>> double_if_positive: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.map_successes_to_result(_double_if_positive)
        >>> double_if_positive(("success", [1, 2]))
        ('success', [2, 4])
        >>> double_if_positive(("success", [1, -1, 2]))
        ('failure', 'bad')
        >>> double_if_positive(("failure", "oops"))
        ('failure', 'oops')
    """
    return map_successes_to_result_sequence(compose2((f, construct_from_result)))


def map_successes_to_result_sequence(
    f: Callable[[_S1], ResultSequence[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S2]]:
    """Create function that maps each element of a [trcks.SuccessSequence][]
    to new [trcks.ResultSequence][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps each element of a [trcks.SuccessSequence][] to new
            [trcks.ResultSequence][] values according to the given function,
            returning the first [trcks.Failure][] returned by `f`, if any.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _expand_if_positive(n: int) -> ResultSequence[str, int]:
        ...     if n > 0:
        ...         return ("success", [n, -n])
        ...     return ("failure", "bad")
        ...
        >>> expand_if_positive: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.map_successes_to_result_sequence(_expand_if_positive)
        >>> expand_if_positive(("success", [1, 2]))
        ('success', [1, -1, 2, -2])
        >>> expand_if_positive(("success", [1, -1, 2]))
        ('failure', 'bad')
        >>> expand_if_positive(("failure", "oops"))
        ('failure', 'oops')
    """

    def partially_mapped_f(s1s: Sequence[_S1]) -> ResultSequence[_F2, _S2]:
        s2s: list[_S2] = []
        for s1 in s1s:
            rs = f(s1)
            match rs[0]:
                case "failure":
                    return rs
                case "success":
                    s2s.extend(rs[1])
                case _:  # pragma: no cover
                    return assert_never(rs[0])  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
        return "success", s2s

    def mapped_f(rs: ResultSequence[_F1, _S1]) -> ResultSequence[_F1 | _F2, _S2]:
        match rs[0]:
            case "failure":
                return rs
            case "success":
                return partially_mapped_f(rs[1])
            case _:  # pragma: no cover
                return assert_never(rs[0])  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]

    return mapped_f


def map_successes_to_sequence(
    f: Callable[[_S1], Sequence[_S2]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S2]]:
    """Create function that maps each element of a [trcks.SuccessSequence][]
    to a [collections.abc.Sequence][].

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            flat-maps each element of a [trcks.SuccessSequence][] to a
            [collections.abc.Sequence][] according to the given function.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _duplicate(n: int) -> list[int]:
        ...     return [n, -n]
        ...
        >>> duplicate: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.map_successes_to_sequence(_duplicate)
        >>> duplicate(("success", [1, 2]))
        ('success', [1, -1, 2, -2])
        >>> duplicate(("failure", "not found"))
        ('failure', 'not found')
    """
    return r.map_success(s.map_to_sequence(f))


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S1]]:
    """Create function that applies a side effect to [trcks.Failure][] values.

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and
            returns the original [trcks.Failure][] value.
            Passes on [trcks.SuccessSequence][] values without side effects.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _print_error(e: str) -> None:
        ...     print(f"Error: {e}")
        ...
        >>> print_error: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.tap_failure(_print_error)
        >>> print_error(("failure", "oops"))
        Error: oops
        ('failure', 'oops')
        >>> print_error(("success", [1]))
        ('success', [1])
    """
    return r.tap_failure(f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F1, Sequence[_S1] | Sequence[_S2]]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to [trcks.Failure][] values.

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned (wrapped as a sequence).
            Passes on [trcks.SuccessSequence][] values without side effects.

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks import Result, ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _retry_lookup(e: str) -> Result[None, int]:
        ...     if e == "not found":
        ...         print("Retrying...")
        ...         return ("success", 42)
        ...     return ("failure", None)
        >>> retry_lookup: Callable[
        ...     [ResultSequence[str, int]], Result[str, Sequence[int]]
        ... ] = rs.tap_failure_to_result(_retry_lookup)
        >>> retry_lookup(("failure", "not found"))
        Retrying...
        ('success', [42])
        >>> retry_lookup(("failure", "fatal"))
        ('failure', 'fatal')
        >>> retry_lookup(("success", [1, 2]))
        ('success', [1, 2])
    """
    composed_f: Callable[[_F1], ResultSequence[object, _S2]] = compose2(
        (f, construct_from_result)
    )
    return tap_failure_to_result_sequence(composed_f)


def tap_failure_to_result_sequence(
    f: Callable[[_F1], ResultSequence[object, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F1, Sequence[_S1] | Sequence[_S2]]]:
    """Create function that applies a side effect with return type
    [trcks.ResultSequence][] to [trcks.Failure][] values.

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned.
            Passes on [trcks.SuccessSequence][] values without side effects.

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks import Result, ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _recover_if_retryable(e: str) -> ResultSequence[None, int]:
        ...     if e == "retry":
        ...         return ("success", [99])
        ...     return ("failure", None)
        ...
        >>> recover_if_retryable: Callable[
        ...     [ResultSequence[str, int]], Result[str, Sequence[int]]
        ... ] = rs.tap_failure_to_result_sequence(_recover_if_retryable)
        >>> recover_if_retryable(("failure", "retry"))
        ('success', [99])
        >>> recover_if_retryable(("failure", "fatal"))
        ('failure', 'fatal')
    """
    return r.tap_failure_to_result(f)


def tap_failure_to_sequence(
    f: Callable[[_F1], Sequence[object]],
) -> Callable[[ResultSequence[_F1, _S1]], SuccessSequence[_F1] | SuccessSequence[_S1]]:
    """Create function that applies a sequence-returning side effect
    to [trcks.Failure][] values.

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and converts them
            to [trcks.SuccessSequence][] values containing the original failure
            repeated once per element in the sequence returned by the side effect.
            Passes on [trcks.SuccessSequence][] values without side effects.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence, SuccessSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _log_and_alert(e: str) -> list[None]:
        ...     return [print(f"Error logged: {e}"), print(f"Alert sent: {e}")]
        ...
        >>> log_and_alert: Callable[
        ...     [ResultSequence[str, int]],
        ...     SuccessSequence[str] | SuccessSequence[int],
        ... ] = rs.tap_failure_to_sequence(_log_and_alert)
        >>> log_and_alert(("failure", "critical"))
        Error logged: critical
        Alert sent: critical
        ('success', ['critical', 'critical'])
        >>> log_and_alert(("success", [1, 2]))
        ('success', [1, 2])
    """

    def tapped_f(f1: _F1) -> Sequence[_F1]:
        return [f1 for _s2 in f(f1)]

    return map_failure_to_sequence(tapped_f)


def tap_successes(
    f: Callable[[_S1], object],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S1]]:
    """Create function that applies a side effect to each element
    of a [trcks.SuccessSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessSequence][] and returns the original
            [trcks.SuccessSequence][].
    """
    return r.map_success(s.tap(f))


def tap_successes_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to each element of a [trcks.SuccessSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessSequence][].
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.SuccessSequence][] element is returned.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import Result, ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _validate_positive(n: int) -> Result[str, None]:
        ...     if n > 0:
        ...         return ("success", None)
        ...     return ("failure", "bad")
        ...
        >>> validate_positive: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.tap_successes_to_result(_validate_positive)
        >>> validate_positive(("success", [1, 2]))
        ('success', [1, 2])
        >>> validate_positive(("success", [1, -1, 2]))
        ('failure', 'bad')
        >>> validate_positive(("failure", "oops"))
        ('failure', 'oops')
    """
    composed_f: Callable[[_S1], ResultSequence[_F2, object]] = compose2(
        (f, construct_from_result)
    )
    return tap_successes_to_result_sequence(composed_f)


def tap_successes_to_result_sequence(
    f: Callable[[_S1], ResultSequence[_F2, object]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type
    [trcks.ResultSequence][] to each element of a [trcks.SuccessSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessSequence][].
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessSequence][],
            *the original* [trcks.SuccessSequence][] element is repeated once
            per element in the side effect output.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _validate_positive_twice(n: int) -> ResultSequence[str, None]:
        ...     if n > 0:
        ...         return ("success", [None, None])
        ...     return ("failure", "bad")
        ...
        >>> validate_positive_twice: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.tap_successes_to_result_sequence(_validate_positive_twice)
        >>> validate_positive_twice(("success", [7]))
        ('success', [7, 7])
        >>> validate_positive_twice(("success", [1, -1]))
        ('failure', 'bad')
    """

    def tapped_f(s1: _S1) -> ResultSequence[_F2, _S1]:
        rs = f(s1)
        match rs[0]:
            case "failure":
                return rs
            case "success":
                return "success", [s1 for _s2 in rs[1]]
            case _:  # pragma: no cover
                return assert_never(rs[0])  # type: ignore[unreachable] # pyright: ignore[reportUnreachable]

    return map_successes_to_result_sequence(tapped_f)


def tap_successes_to_sequence(
    f: Callable[[_S1], Sequence[object]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S1]]:
    """Create function that applies a sequence-returning side effect
    to each element of a [trcks.SuccessSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessSequence][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessSequence][]
            and repeats each original element once per element in the sequence
            returned by the side effect.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultSequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def _print_twice(n: int) -> list[None]:
        ...     return [print(f"v={n}"), print(f"v={n}")]
        ...
        >>> print_twice: Callable[
        ...     [ResultSequence[str, int]], ResultSequence[str, int]
        ... ] = rs.tap_successes_to_sequence(_print_twice)
        >>> print_twice(("success", [7]))
        v=7
        v=7
        ('success', [7, 7])
    """
    return r.map_success(s.tap_to_sequence(f))
