"""Monadic functions for [collections.abc.Sequence][].

Provides utilities for functional composition of
functions returning [collections.abc.Sequence][] values.

Example:
    Create and process a [collections.abc.Sequence][]:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import sequence as s
    >>> def double(n: int) -> int:
    ...     return n * 2
    ...
    >>> def log(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> result = pipe(
    ...     (
    ...         [1, 2, 3],
    ...         s.map_(double),
    ...         s.tap(log),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> result
    [2, 4, 6]

    Map each element to a sequence and flatten the result:

    >>> def duplicate(n: int) -> list[int]:
    ...     return [n, n]
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
    """Create a [collections.abc.Sequence][] from a single value.

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
    """Create function that maps [collections.abc.Sequence][]s to
    [collections.abc.Sequence][]s of the same length.

    Args:
        f: Function to apply to each element.

    Returns:
        Maps [collections.abc.Sequence][]s to [collections.abc.Sequence][]s
            of the same length according to the given function.

    Note:
        The underscore in the function name helps to avoid collisions
        with the built-in function [map][].

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks.fp.monads import sequence as s
        >>> def double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> double_integers: Callable[
        ...     [Sequence[int]], Sequence[int]
        ... ] = s.map_(double_integer)
        >>> double_integers([1, 2, 3])
        [2, 4, 6]
        >>> double_integers((1, 2, 3))
        [2, 4, 6]
    """
    return map_to_sequence(compose2((f, construct)))


def map_to_sequence(
    f: Callable[[_T1], Sequence[_T2]],
) -> Callable[[Sequence[_T1]], Sequence[_T2]]:
    """Create function that maps [collections.abc.Sequence][]s to
    [collections.abc.Sequence][]s of varying length.

    Args:
        f: Function to apply to each element that returns a
            [collections.abc.Sequence][].

    Returns:
        Maps [collections.abc.Sequence][]s to [collections.abc.Sequence][]s
            of varying length according to the given function.

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks.fp.monads import sequence as s
        >>> def duplicate_integer(n: int) -> list[int]:
        ...     return [n, n]
        ...
        >>> duplicate_integers: Callable[
        ...     [Sequence[int]], Sequence[int]
        ... ] = s.map_to_sequence(duplicate_integer)
        >>> duplicate_integers([1, 2, 3])
        [1, 1, 2, 2, 3, 3]
    """

    def mapped_f(t1s: Sequence[_T1]) -> Sequence[_T2]:
        return [t2 for t1 in t1s for t2 in f(t1)]

    return mapped_f


def tap(
    f: Callable[[_T1], object],
) -> Callable[[Sequence[_T1]], Sequence[_T1]]:
    """Create function that applies a side effect to each element
    of a [collections.abc.Sequence][].

    Args:
        f: Side effect to apply to each element.

    Returns:
        Applies the given side effect to each element of a
            [collections.abc.Sequence][] and returns the original
            [collections.abc.Sequence][].

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks.fp.monads import sequence as s
        >>> def log(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> log_and_pass: Callable[[Sequence[int]], Sequence[int]] = s.tap(log)
        >>> result = log_and_pass([1, 2, 3])
        Received: 1
        Received: 2
        Received: 3
        >>> result
        [1, 2, 3]
    """
    return map_(i.tap(f))


def tap_to_sequence(
    f: Callable[[_T1], Sequence[object]],
) -> Callable[[Sequence[_T1]], Sequence[_T1]]:
    """Create function that applies a side effect with return type
    [collections.abc.Sequence][] to each element of a
    [collections.abc.Sequence][].

    Args:
        f: Side effect to apply to each element that returns a
            [collections.abc.Sequence][].

    Returns:
        Applies the given side effect to each element of a
            [collections.abc.Sequence][]. Returns each element as
            many times as the side effect returns elements.

    Example:
        >>> from collections.abc import Callable, Sequence
        >>> from trcks.fp.monads import sequence as s
        >>> def get_divisors(n: int) -> list[int]:
        ...     return [d for d in range(1, n + 1) if n % d == 0]
        ...
        >>> get_and_pass: Callable[
        ...     [Sequence[int]], Sequence[int]
        ... ] = s.tap_to_sequence(get_divisors)
        >>> result = get_and_pass([2, 4])
        >>> result
        [2, 2, 4, 4, 4]
    """

    def bypassed_f(t1: _T1) -> Sequence[_T1]:
        return [t1 for _t2 in f(t1)]

    return map_to_sequence(bypassed_f)
