"""Monadic functions for [trcks.ResultSequence][].

Provides utilities for functional composition of
[trcks.ResultSequence][] values.

Example:
    Map and tap each element inside a success sequence:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result as r
    >>> from trcks.fp.monads import result_sequence as rs
    >>> p = (
    ...     rs.construct_successes_from_sequence([1, 2, 3]),
    ...     rs.map_successes(lambda x: x * 2),
    ...     rs.tap_successes(lambda x: print(f"Processed: {x}")),
    ...     rs.map_successes_to_sequence(lambda x: [x, -x]),
    ... )
    >>> pipe(p)
    Processed: 2
    Processed: 4
    Processed: 6
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
        >>> from trcks.fp.monads import result as r
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_from_result(r.construct_success(7))
        ('success', [7])
        >>> rs.construct_from_result(r.construct_failure("oops"))
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
    """Map [trcks.Failure][] values in a [trcks.ResultSequence][].

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to apply to the failure value.

    Returns:
        Function that transforms failures and
        passes through [trcks.SuccessSequence][] values.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> add_prefix = rs.map_failure(lambda e: f"err: {e}")
        >>> add_prefix(("failure", "not found"))
        ('failure', 'err: not found')
        >>> add_prefix(("success", [1, 2]))
        ('success', [1, 2])
    """
    return r.map_failure(f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F2, Sequence[_S1] | Sequence[_S2]]]:
    """Map [trcks.Failure][] values in a [trcks.ResultSequence][]
    to [trcks.Result][] values.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to transform the failure into a new [trcks.Result][].

    Returns:
        Function that maps failures to new [trcks.Result][] values
            and leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> recover = rs.map_failure_to_result(
        ...     lambda e: ("success", 0) if e == "not found" else ("failure", e)
        ... )
        >>> recover(("failure", "not found"))
        ('success', [0])
        >>> recover(("success", [1, 2]))
        ('success', [1, 2])
    """
    return map_failure_to_result_sequence(compose2((f, construct_from_result)))


def map_failure_to_result_sequence(
    f: Callable[[_F1], ResultSequence[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F2, Sequence[_S1] | Sequence[_S2]]]:
    """Map [trcks.Failure][] values in a [trcks.ResultSequence][] to new values.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to transform the failure into a new [trcks.ResultSequence][].

    Returns:
        Function that maps failures to new [trcks.ResultSequence][] values
            and leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> recover = rs.map_failure_to_result_sequence(
        ...     lambda e: ("success", [0]) if e == "not found" else ("failure", e)
        ... )
        >>> recover(("failure", "not found"))
        ('success', [0])
        >>> recover(("success", [1, 2]))
        ('success', [1, 2])
    """
    return r.map_failure_to_result(f)


def map_failure_to_sequence(
    f: Callable[[_F1], Sequence[_S2]],
) -> Callable[[ResultSequence[_F1, _S1]], SuccessSequence[_S1] | SuccessSequence[_S2]]:
    """Map [trcks.Failure][] values in a [trcks.ResultSequence][] to sequences.

    [trcks.SuccessSequence][] values are left unchanged.

    Args:
        f: Function to transform the failure into a sequence.

    Returns:
        Function that maps failures to sequences wrapped in a [trcks.Success][]
            and leaves [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> recover = rs.map_failure_to_sequence(
        ...     lambda e: [0] if e == "not found" else []
        ... )
        >>> recover(("failure", "not found"))
        ('success', [0])
        >>> recover(("success", [1, 2]))
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
    """Map a synchronous function over each element in a [trcks.ResultSequence][].

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each success element.

    Returns:
        Function that transforms [trcks.SuccessSequence][] values
            element-wise.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> double = rs.map_successes(lambda x: x * 2)
        >>> double(("success", [1, 2, 3]))
        ('success', [2, 4, 6])
        >>> double(("failure", "not found"))
        ('failure', 'not found')
    """
    return r.map_success(s.map_(f))


def map_successes_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S2]]:
    """Map a result-returning function over each element in a [trcks.ResultSequence][].

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function returning a [trcks.Result][] for each success element.

    Returns:
        Function that maps over [trcks.SuccessSequence][] values and
            returns the first [trcks.Failure][] encountered, if any.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> check = rs.map_successes_to_result(
        ...     lambda x: ("success", x * 2) if x > 0 else ("failure", "bad")
        ... )
        >>> check(("success", [1, 2]))
        ('success', [2, 4])
        >>> check(("success", [1, -1, 2]))
        ('failure', 'bad')
        >>> check(("failure", "oops"))
        ('failure', 'oops')
    """
    return map_successes_to_result_sequence(compose2((f, construct_from_result)))


def map_successes_to_result_sequence(
    f: Callable[[_S1], ResultSequence[_F2, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S2]]:
    """Map a sequence-returning result function over a [trcks.ResultSequence][].

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function returning a [trcks.ResultSequence][] for each success element.

    Returns:
        Function that flat-maps [trcks.SuccessSequence][] values and
            short-circuits on the first [trcks.Failure][] returned by `f`.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> expand = rs.map_successes_to_result_sequence(
        ...     lambda x: ("success", [x, -x]) if x > 0 else ("failure", "bad")
        ... )
        >>> expand(("success", [1, 2]))
        ('success', [1, -1, 2, -2])
        >>> expand(("success", [1, -1, 2]))
        ('failure', 'bad')
        >>> expand(("failure", "oops"))
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
    """Map a sequence-returning function over elements in a [trcks.ResultSequence][].

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function returning a sequence for each success element.

    Returns:
        Function that flat-maps over [trcks.SuccessSequence][] values.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> flat = rs.map_successes_to_sequence(lambda x: [x, -x])
        >>> flat(("success", [1, 2]))
        ('success', [1, -1, 2, -2])
    """
    return r.map_success(s.map_to_sequence(f))


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S1]]:
    """Apply a synchronous side effect to [trcks.Failure][] values
    in a [trcks.ResultSequence][].

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side-effect function to apply to the failure value.

    Returns:
        Function that applies the side effect to failures and passes through
            [trcks.SuccessSequence][] values unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> log_err = rs.tap_failure(lambda e: print(f"Error: {e}"))
        >>> log_err(("failure", "oops"))
        Error: oops
        ('failure', 'oops')
        >>> log_err(("success", [1]))
        ('success', [1])
    """
    return r.tap_failure(f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F1, Sequence[_S1] | Sequence[_S2]]]:
    """Apply a side effect with return type [trcks.Result][]
    to [trcks.Failure][] values in a [trcks.ResultSequence][].

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side-effect function returning a [trcks.Result][].

    Returns:
        Function that applies the side effect to failures.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned (wrapped as a sequence).
            [trcks.SuccessSequence][] values are passed through unchanged.

    Example:
        >>> from trcks import Result
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def retry_lookup(e: str) -> Result[None, int]:
        ...     if e == "not found":
        ...         print("Retrying...")
        ...         return ("success", 42)
        ...     return ("failure", None)
        >>> recover = rs.tap_failure_to_result(retry_lookup)
        >>> recover(("failure", "not found"))
        Retrying...
        ('success', [42])
        >>> recover(("failure", "fatal"))
        ('failure', 'fatal')
        >>> recover(("success", [1, 2]))
        ('success', [1, 2])
    """
    composed_f: Callable[[_F1], ResultSequence[object, _S2]] = compose2(
        (f, construct_from_result)
    )
    return tap_failure_to_result_sequence(composed_f)


def tap_failure_to_result_sequence(
    f: Callable[[_F1], ResultSequence[object, _S2]],
) -> Callable[[ResultSequence[_F1, _S1]], Result[_F1, Sequence[_S1] | Sequence[_S2]]]:
    """Apply a side effect with return type [trcks.ResultSequence][]
    to [trcks.Failure][] values in a [trcks.ResultSequence][].

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side-effect function returning a [trcks.ResultSequence][].

    Returns:
        Function that applies the side effect to failures.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned.
            [trcks.SuccessSequence][] values are passed through unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> attempt_recover = rs.tap_failure_to_result_sequence(
        ...     lambda e: ("success", [99]) if e == "retry" else ("failure", None)
        ... )
        >>> attempt_recover(("failure", "retry"))
        ('success', [99])
        >>> attempt_recover(("failure", "fatal"))
        ('failure', 'fatal')
    """
    return r.tap_failure_to_result(f)


def tap_failure_to_sequence(
    f: Callable[[_F1], Sequence[object]],
) -> Callable[[ResultSequence[_F1, _S1]], SuccessSequence[_F1] | SuccessSequence[_S1]]:
    """Apply a sequence-returning side effect to [trcks.Failure][] values
    in a [trcks.ResultSequence][].

    The number of side-effect outputs determines how many times the original
    failure value is repeated. The failure is converted to a [trcks.SuccessSequence][].

    [trcks.SuccessSequence][] values are passed on without side effects.

    Args:
        f: Side-effect function returning a sequence.

    Returns:
        Function that applies the side effect to failures and converts them
            to [trcks.SuccessSequence][] values containing the original failure
            repeated once per element in the sequence returned by the side effect.
            [trcks.SuccessSequence][] values are passed through unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> log_err = rs.tap_failure_to_sequence(
        ...     lambda e: [print(f"Error logged: {e}"), print(f"Alert sent: {e}")]
        ... )
        >>> log_err(("failure", "critical"))
        Error logged: critical
        Alert sent: critical
        ('success', ['critical', 'critical'])
        >>> log_err(("success", [1, 2]))
        ('success', [1, 2])
    """

    def tapped_f(f1: _F1) -> Sequence[_F1]:
        return [f1 for _s2 in f(f1)]

    return map_failure_to_sequence(tapped_f)


def tap_successes(
    f: Callable[[_S1], object],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1, _S1]]:
    """Apply a synchronous side effect to each element in a [trcks.ResultSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side-effect function to apply to each success element.

    Returns:
        Function that applies the side effect and returns the original
            [trcks.ResultSequence][] value.
    """
    return r.map_success(s.tap(f))


def tap_successes_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S1]]:
    """Apply a side effect with return type [trcks.Result][]
    to each element in a [trcks.ResultSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side-effect function returning a [trcks.Result][].

    Returns:
        Function that applies the side effect to each success element.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.SuccessSequence][] element is returned.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> audit = rs.tap_successes_to_result(
        ...     lambda x: ("success", None) if x > 0 else ("failure", "bad")
        ... )
        >>> audit(("success", [1, 2]))
        ('success', [1, 2])
        >>> audit(("success", [1, -1, 2]))
        ('failure', 'bad')
        >>> audit(("failure", "oops"))
        ('failure', 'oops')
    """
    composed_f: Callable[[_S1], ResultSequence[_F2, object]] = compose2(
        (f, construct_from_result)
    )
    return tap_successes_to_result_sequence(composed_f)


def tap_successes_to_result_sequence(
    f: Callable[[_S1], ResultSequence[_F2, object]],
) -> Callable[[ResultSequence[_F1, _S1]], ResultSequence[_F1 | _F2, _S1]]:
    """Apply a side effect with return type [trcks.ResultSequence][]
    to each element in a [trcks.ResultSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side-effect function returning a [trcks.ResultSequence][].

    Returns:
        Function that applies the side effect to each success element.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessSequence][],
            *the original* [trcks.SuccessSequence][] element is repeated once
            per element in the side effect output.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> audit = rs.tap_successes_to_result_sequence(
        ...     lambda x: ("success", [None, None]) if x > 0 else ("failure", "bad")
        ... )
        >>> audit(("success", [7]))
        ('success', [7, 7])
        >>> audit(("success", [1, -1]))
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
    """Apply a sequence-returning side effect to each element
    in a [trcks.ResultSequence][].

    The number of side-effect outputs determines how many times each original
    element is repeated in the resulting [trcks.ResultSequence][].

    [trcks.Failure][] values are passed on without side effects.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> log_mult = rs.tap_successes_to_sequence(
        ...     lambda x: [print(f"v={x}"), print(f"v={x}")]
        ... )
        >>> log_mult(("success", [7]))
        v=7
        v=7
        ('success', [7, 7])
    """
    return r.map_success(s.tap_to_sequence(f))
