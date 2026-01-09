"""Monadic functions for [trcks.Result][] of [collections.abc.Sequence][].

Provides utilities for functional composition of
synchronous [trcks.Result][]-returning functions whose success value
is a [collections.abc.Sequence][].

Example:
    Map and tap each element inside a success sequence:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result as r
    >>> from trcks.fp.monads import result_sequence as rs
    >>> p = (
    ...     rs.construct_success_from_sequence((1, 2, 3)),
    ...     rs.map_success(lambda x: x * 2),
    ...     rs.tap_success(lambda x: print(f"Processed: {x}")),
    ...     rs.map_success_to_sequence(lambda x: (x, -x)),
    ... )
    >>> pipe(p)
    Processed: 2
    Processed: 4
    Processed: 6
    ('success', [2, -2, 4, -4, 6, -6])

    Validate or transform the whole success sequence as a single value:

    >>> from collections.abc import Sequence
    >>> from trcks import Result
    >>> def non_empty(seq: Sequence[int]) -> Result[str, Sequence[int]]:
    ...     return ("success", seq) if seq else ("failure", "empty")
    ...
    >>> p2 = (
    ...     rs.construct_success_from_sequence(()),
    ...     rs.map_success(lambda x: x + 1),
    ...     rs.map_success_to_result(non_empty),
    ...     rs.tap_failure(lambda f: print(f"Validation failed: {f}")),
    ... )
    >>> pipe(p2)
    Validation failed: empty
    ('failure', 'empty')
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.monads import result as r
from trcks.fp.monads import sequence as s

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable, Sequence

    from trcks import Failure, Result, Success

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


def construct_success(value: _S) -> Success[Sequence[_S]]:
    """Create a [trcks.Success][] of a single-element sequence from a value.

    Args:
        value: Value to be wrapped inside the success sequence.

    Returns:
        [trcks.Success][] containing a one-element [collections.abc.Sequence][].

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_success(42)
        ('success', [42])
    """
    return r.construct_success(s.construct(value))


def construct_success_from_sequence(seq: Sequence[_S]) -> Success[Sequence[_S]]:
    """Create a [trcks.Success][] from an existing sequence.

    Args:
        seq: The sequence to wrap inside the success value.

    Returns:
        [trcks.Success][] containing the given [collections.abc.Sequence][].

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_success_from_sequence((1, 2))
        ('success', (1, 2))
    """
    return r.construct_success(seq)


def construct_from_result(rslt: Result[_F, _S]) -> Result[_F, Sequence[_S]]:
    """Lift a [trcks.Result][] value into a result of sequence.

    Maps success values `S` to single-element sequences `Sequence[S]`.

    Args:
        rslt: The input [trcks.Result][].

    Returns:
        The lifted [trcks.Result][] with success payload wrapped in a sequence.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> from trcks.fp.monads import result_sequence as rs
        >>> rs.construct_from_result(r.construct_success(7))
        ('success', [7])
        >>> rs.construct_from_result(r.construct_failure("oops"))
        ('failure', 'oops')
    """
    return r.map_success(s.construct)(rslt)


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F2, Sequence[_S1]]]:
    """Map [trcks.Failure][] values; leave success sequences unchanged.

    Args:
        f: Function to apply to the failure value.

    Returns:
        Function that transforms failures and passes through success sequences.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> add_prefix = rs.map_failure(lambda e: f"err: {e}")
        >>> add_prefix(("failure", "not found"))
        ('failure', 'err: not found')
        >>> add_prefix(("success", (1, 2)))
        ('success', (1, 2))
    """
    return r.map_failure(f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, Sequence[_S2]]],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F2, Sequence[_S1] | Sequence[_S2]]]:
    """Map failures to a new [trcks.Result][]; success sequences unchanged.

    Args:
        f: Function to transform the failure into a new result.

    Returns:
        Function that maps failures to failures or success sequences
        and leaves success sequences unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> recover = rs.map_failure_to_result(
        ...     lambda e: ("success", (0,)) if e == "not found" else ("failure", e)
        ... )
        >>> recover(("failure", "not found"))
        ('success', (0,))
        >>> recover(("success", (1, 2)))
        ('success', (1, 2))
    """
    return r.map_failure_to_result(f)


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1, Sequence[_S1]]]:
    """Apply a side effect to failures; pass through results unchanged otherwise.

    Args:
        f: Side-effect function to apply to the failure value.

    Returns:
        Function that applies the side effect to failures and passes through
        success sequences unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> log_err = rs.tap_failure(lambda e: print(f"Error: {e}"))
        >>> log_err(("failure", "oops"))
        Error: oops
        ('failure', 'oops')
        >>> log_err(("success", (1,)))
        ('success', (1,))
    """
    return r.tap_failure(f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, Sequence[_S2]]],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1, Sequence[_S1] | Sequence[_S2]]]:
    """Apply a [trcks.Result][]-returning side effect to failures.

    If the side effect returns a failure, the original failure is kept.
    If it returns a success, that success is returned.
    Success sequences are passed through unchanged.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> attempt_recover = rs.tap_failure_to_result(
        ...     lambda e: ("success", (99,)) if e == "retry" else ("failure", None)
        ... )
        >>> attempt_recover(("failure", "retry"))
        ('success', (99,))
        >>> attempt_recover(("failure", "fatal"))
        ('failure', 'fatal')
    """
    return r.tap_failure_to_result(f)


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1, Sequence[_S2]]]:
    """Map a function over each element of a success sequence.

    Args:
        f: Function to apply to each success element.

    Returns:
        Function that transforms success sequences element-wise.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> double = rs.map_success(lambda x: x * 2)
        >>> double(("success", (1, 2, 3)))
        ('success', [2, 4, 6])
        >>> double(("failure", "not found"))
        ('failure', 'not found')
    """
    return r.map_success(s.map_(f))


def map_success_to_sequence(
    f: Callable[[_S1], Sequence[_S2]],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1, Sequence[_S2]]]:
    """Map a sequence-returning function and flatten inside success.

    Args:
        f: Function returning a sequence for each success element.

    Returns:
        Function that flat-maps over success sequences.

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> flat = rs.map_success_to_sequence(lambda x: (x, -x))
        >>> flat(("success", (1, 2)))
        ('success', [1, -1, 2, -2])
    """
    return r.map_success(s.map_to_sequence(f))


def tap_success(
    f: Callable[[_S1], object],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1, Sequence[_S1]]]:
    """Apply a side effect to each element of a success sequence.

    Args:
        f: Side-effect function to apply to each success element.

    Returns:
        Function that applies the side effect and returns original sequence.
    """
    return r.map_success(s.tap(f))


def tap_success_to_sequence(
    f: Callable[[_S1], Sequence[object]],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1, Sequence[_S1]]]:
    """Apply a sequence-returning side effect per element; pass through values.

    The side effect controls how many times each element is replicated
    in the output sequence, similar to [tap_to_sequence][].

    Example:
        >>> from trcks.fp.monads import result_sequence as rs
        >>> log_mult = rs.tap_success_to_sequence(
        ...     lambda x: [print(f"v={x}"), print(f"v={x}")]
        ... )
        >>> log_mult(("success", (7,)))
        v=7
        v=7
        ('success', [7, 7])
    """
    return r.map_success(s.tap_to_sequence(f))


def map_success_to_result(
    f: Callable[[Sequence[_S1]], Result[_F2, Sequence[_S2]]],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1 | _F2, Sequence[_S2]]]:
    """Transform the whole success sequence via a [trcks.Result][]-returning function.

    Args:
        f: Function operating on the entire success sequence.

    Returns:
        Function that maps success to a new result, failures unchanged.

    Example:
        >>> from trcks import Result
        >>> from collections.abc import Sequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def validate_len(seq: Sequence[int]) -> Result[str, Sequence[int]]:
        ...     return ("success", seq) if len(seq) > 0 else ("failure", "empty")
        >>> check = rs.map_success_to_result(validate_len)
        >>> check(("success", (1, 2)))
        ('success', (1, 2))
        >>> check(("success", ()))
        ('failure', 'empty')
    """
    return r.map_success_to_result(f)


def tap_success_to_result(
    f: Callable[[Sequence[_S1]], Result[_F2, object]],
) -> Callable[[Result[_F1, Sequence[_S1]]], Result[_F1 | _F2, Sequence[_S1]]]:
    """Apply a [trcks.Result][]-returning side effect to the whole success sequence.

    On success, returns the original success sequence; on failure, returns
    the failure produced by the side effect.

    Example:
        >>> from trcks import Result
        >>> from collections.abc import Sequence
        >>> from trcks.fp.monads import result_sequence as rs
        >>> def persist(seq: Sequence[int]) -> Result[str, None]:
        ...     if len(seq) < 10:
        ...         print(f"Saved {len(seq)} items")
        ...         return ("success", None)
        ...     return ("failure", "too large")
        >>> save = rs.tap_success_to_result(persist)
        >>> save(("success", (1, 2)))
        Saved 2 items
        ('success', (1, 2))
    """
    return r.tap_success_to_result(f)
