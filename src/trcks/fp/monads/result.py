"""Monadic functions for [trcks.Result][].

Provides utilities for functional composition of
synchronous [trcks.Result][]-returning functions.

Example:
    Create and process a value of type [trcks.Result][]:

    >>> import math
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result as r
    >>> rslt = pipe(
    ...     (
    ...         r.construct_success(1_000_000.0),
    ...         r.tap_success(lambda x: print(f"Processing value {x} ...")),
    ...         r.map_success_to_result(
    ...             lambda x: (
    ...                 ("success", math.sqrt(x))
    ...                 if x >= 0
    ...                 else ("failure", "negative value")
    ...             )
    ...         ),
    ...         r.tap_success_to_result(
    ...             lambda x: (
    ...                 ("success", print(f"Wrote result {x} to disk."))
    ...                 if x < 100
    ...                 else ("failure", "out of disk space")
    ...             )
    ...         ),
    ...     )
    ... )
    Processing value 1000000.0 ...
    >>> rslt
    ('failure', 'out of disk space')

    If your static type checker cannot infer the type of
    the argument passed to [trcks.fp.composition.pipe][],
    you can explicitly assign a type:

    >>> import math
    >>> from trcks import Result, Success
    >>> from trcks.fp.composition import Pipeline3, pipe
    >>> from trcks.fp.monads import result as r
    >>> p: Pipeline3[
    ...     Success[float],
    ...     Result[str, float],
    ...     Result[str, float],
    ...     Result[str, float],
    ... ] = (
    ...     r.construct_success(1_000_000.0),
    ...     r.tap_success(lambda x: print(f"Processing value {x} ...")),
    ...     r.map_success_to_result(
    ...         lambda x: (
    ...             ("success", math.sqrt(x))
    ...             if x >= 0
    ...             else ("failure", "negative value")
    ...         )
    ...     ),
    ...     r.tap_success_to_result(
    ...         lambda x: (
    ...             ("success", print(f"Wrote result {x} to disk."))
    ...             if x < 100
    ...             else ("failure", "out of disk space")
    ...         )
    ...     ),
    ... )
    >>> rslt = pipe(p)
    Processing value 1000000.0 ...
    >>> rslt
    ('failure', 'out of disk space')
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, assert_never
from trcks.fp.monads import identity as i

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

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
        value: Value to be wrapped in a [trcks.Failure][] object.

    Returns:
        [trcks.Failure][] object containing the given value.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> r.construct_failure(42)
        ('failure', 42)
    """
    return "failure", value


def construct_success(value: _S) -> Success[_S]:
    """Create a [trcks.Success][] object from a value.

    Args:
        value: Value to be wrapped in a [trcks.Success][] object.

    Returns:
        [trcks.Success][] object containing the given value.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> r.construct_success(42)
        ('success', 42)
    """
    return "success", value


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1]]:
    """Create function that maps [trcks.Failure][] values to [trcks.Failure][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.Failure][] values
            according to the given function and
            leaves [trcks.Success][] values unchanged.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> add_prefix_to_failure = r.map_failure(lambda s: f"Prefix: {s}")
        >>> add_prefix_to_failure(("failure", "negative value"))
        ('failure', 'Prefix: negative value')
        >>> add_prefix_to_failure(("success", 25.0))
        ('success', 25.0)
    """

    def composed_f(value: _F1) -> Failure[_F2]:
        return construct_failure(f(value))

    return map_failure_to_result(composed_f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to [trcks.Failure][] and [trcks.Success][] values
            according to the given function and
            leaves [trcks.Success][] values unchanged.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> replace_not_found_failure_by_default_value = r.map_failure_to_result(
        ...     lambda s: ("success", 0.0) if s == "not found" else ("failure", s)
        ... )
        >>> replace_not_found_failure_by_default_value(("failure", "not found"))
        ('success', 0.0)
        >>> replace_not_found_failure_by_default_value(("failure", "other failure"))
        ('failure', 'other failure')
        >>> replace_not_found_failure_by_default_value(("success", 25.0))
        ('success', 25.0)
    """

    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1 | _S2]:
        if rslt[0] == "failure":
            return f(rslt[1])
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return mapped_f


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values to [trcks.Success][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] value.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to new [trcks.Success][] values
            according to the given function.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> def increase(n: int) -> int:
        ...     return n + 1
        ...
        >>> increase_success = r.map_success(increase)
        >>> increase_success(("failure", "not found"))
        ('failure', 'not found')
        >>> increase_success(("success", 42))
        ('success', 43)
    """

    def composed_f(value: _S1) -> Success[_S2]:
        return construct_success(f(value))

    return map_success_to_result(composed_f)


def map_success_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] value.

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps [trcks.Success][] values to [trcks.Failure][] and
            [trcks.Success][] values according to the given function.

    Example:
        >>> import math
        >>> from trcks import Result
        >>> from trcks.fp.monads import result as r
        >>> def _get_square_root(x: float) -> Result[str, float]:
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", math.sqrt(x)
        ...
        >>> get_square_root = r.map_success_to_result(_get_square_root)
        >>> get_square_root(("failure", "not found"))
        ('failure', 'not found')
        >>> get_square_root(("success", -25.0))
        ('failure', 'negative value')
        >>> get_square_root(("success", 25.0))
        ('success', 5.0)
    """

    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1 | _F2, _S2]:
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return f(rslt[1])
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return mapped_f


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S1]]:
    """Create function that applies a side effect to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and
            returns the original [trcks.Failure][] value.
            Passes on [trcks.Success][] values without side effects.
    """
    return map_failure(i.tap(f))


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S1 | _S2]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] value is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned.
            Passes on [trcks.Success][] values without side effects.
    """

    def bypassed_f(value: _F1) -> Result[_F1, _S2]:
        rslt: Result[object, _S2] = f(value)
        if rslt[0] == "failure":
            return construct_failure(value)
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return map_failure_to_result(bypassed_f)


def tap_success(
    f: Callable[[_S1], object],
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S1]]:
    """Create function that applies a side effect to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Success][] value.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values and
            returns the original [trcks.Success][] value.
    """
    return map_success(i.tap(f))


def tap_success_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[[Result[_F1, _S1]], Result[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Success][] value.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.Success][] value is returned.
    """

    def bypassed_f(value: _S1) -> Result[_F2, _S1]:
        rslt: Result[_F2, object] = f(value)
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return construct_success(value)
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return map_success_to_result(bypassed_f)
