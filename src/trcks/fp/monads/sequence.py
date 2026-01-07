"""Monadic functions for [collections.abc.Sequence][].

Provides utilities for functional composition of
functions returning [collections.abc.Sequence][] values.

Example:
    Create and process a [collections.abc.Sequence][]:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import sequence as s
    >>> def double(x: int) -> int:
    ...     return x * 2
    ...
    >>> result = pipe(
    ...     (
    ...         [1, 2, 3],
    ...         s.map_(double),
    ...         s.tap(lambda x: print(f"Processing value: {x}")),
    ...     )
    ... )
    Processing value: 2
    Processing value: 4
    Processing value: 6
    >>> result
    [2, 4, 6]

    Map each element to a sequence and flatten the result:

    >>> def duplicate(x: int) -> list[int]:
    ...     return [x, x]
    ...
    >>> result = pipe(
    ...     (
    ...         [1, 2, 3],
    ...         s.map_to_sequence(duplicate),
    ...     )
    ... )
    >>> result
    [1, 1, 2, 2, 3, 3]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.composition import compose2
from trcks.fp.monads import identity as i

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

__docformat__ = "google"

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def construct(value: _T) -> Sequence[_T]:
    """Create a [collections.abc.Sequence][] from a value.

    Args:
        value: A single value.

    Returns:
        A [collections.abc.Sequence][] containing the single value.

    Example:
        >>> from trcks.fp.monads import sequence as s
        >>> s.construct(42)
        [42]
    """
    return [value]


def map_(f: Callable[[_T1], _T2]) -> Callable[[Sequence[_T1]], Sequence[_T2]]:
    """Create function that maps a function over each element in a Sequence.

    Args:
        f: Function to apply to each element.

    Returns:
        A function that takes a [collections.abc.Sequence][] and returns
            a new [collections.abc.Sequence][] with the function applied
            to each element.

    Example:
        >>> from trcks.fp.monads import sequence as s
        >>> double = s.map_(lambda x: x * 2)
        >>> double([1, 2, 3])
        [2, 4, 6]
        >>> double((1, 2, 3))
        [2, 4, 6]
    """
    return map_to_sequence(compose2((f, construct)))


def map_to_sequence(
    f: Callable[[_T1], Sequence[_T2]],
) -> Callable[[Sequence[_T1]], Sequence[_T2]]:
    """Create function that maps a function returning a Sequence
    over each element and flattens the result.

    Args:
        f: Function to apply to each element that returns a Sequence.

    Returns:
        A function that takes a Sequence and returns
            a new flattened Sequence with the function
            applied to each element.

    Example:
        >>> from trcks.fp.monads import sequence as s
        >>> duplicate = s.map_to_sequence(lambda x: [x, x])
        >>> duplicate([1, 2, 3])
        [1, 1, 2, 2, 3, 3]
    """

    def mapped_f(t1s: Sequence[_T1]) -> Sequence[_T2]:
        return [t2 for t1 in t1s for t2 in f(t1)]

    return mapped_f


def tap(
    f: Callable[[_T1], object],
) -> Callable[[Sequence[_T1]], Sequence[_T1]]:
    """Create function that applies a side effect to each element in a Sequence.

    Args:
        f: Side effect to apply to each element.

    Returns:
        A function that takes a [collections.abc.Sequence][] and returns
            the same [collections.abc.Sequence][] with the side effect
            applied to each element.

    Example:
        >>> from trcks.fp.monads import sequence as s
        >>> def log(x: int) -> None:
        ...     print(f"Processing: {x}")
        ...
        >>> log_and_pass = s.tap(log)
        >>> result = log_and_pass([1, 2, 3])
        Processing: 1
        Processing: 2
        Processing: 3
        >>> result
        [1, 2, 3]
    """
    return map_(i.tap(f))


def tap_to_sequence(
    f: Callable[[_T1], Sequence[object]],
) -> Callable[[Sequence[_T1]], Sequence[_T1]]:
    """Create function that applies a side effect returning a Sequence
    to each element in a Sequence.

    Args:
        f: Side effect to apply to each element that returns a Sequence.

    Returns:
        A function that takes a [collections.abc.Sequence][] and returns
            the original [collections.abc.Sequence][] with the side effect
            applied to each element.

    Example:
        >>> from trcks.fp.monads import sequence as s
        >>> def write_to_disk(x: int) -> list[str]:
        ...     print(f"Wrote {x} to disk.")
        ...     return [str(x), str(x)]
        ...
        >>> write_and_pass = s.tap_to_sequence(write_to_disk)
        >>> result = write_and_pass([1, 2, 3])
        Wrote 1 to disk.
        Wrote 2 to disk.
        Wrote 3 to disk.
        >>> result
        [1, 1, 2, 2, 3, 3]
    """

    def bypassed_f(t1: _T1) -> Sequence[_T1]:
        return [t1 for _t2 in f(t1)]

    return map_to_sequence(bypassed_f)
