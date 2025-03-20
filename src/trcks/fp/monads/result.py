"""Monadic functions for `trcks.Result`.

Provides utilities for functional composition of `trcks.Result`-returning functions.

Example:
    Create and process a value of type `trcks.Result`:

        >>> import math
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> rslt = pipe((
        ...     r.construct_success(-5.0),
        ...     r.map_success_to_result(
        ...             lambda x:
        ...                 ("success", x)
        ...                 if x >= 0
        ...                 else ("failure", "negative value")
        ...     ),
        ...     r.map_success(math.sqrt),
        ... ))
        >>> rslt
        ('failure', 'negative value')

    If your static type checker cannot infer the type of
    the argument passed to `trcks.fp.composition.pipe`,
    you can explicitly assign a type:

        >>> import math
        >>> from trcks import Result, Success
        >>> from trcks.fp.composition import Pipeline2, pipe
        >>> from trcks.fp.monads import result as r
        >>> p: Pipeline2[Success[float], Result[str, float], Result[str, float]] = (
        ...     r.construct_success(-5.0),
        ...     r.map_success_to_result(
        ...             lambda x:
        ...                 ("success", x)
        ...                 if x >= 0
        ...                 else ("failure", "negative value")
        ...     ),
        ...     r.map_success(math.sqrt),
        ... )
        >>> rslt = pipe(p)
        >>> rslt
        ('failure', 'negative value')
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from trcks._typing import assert_never

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
    """Create a `Failure` object from a value.

    Args:
        value: Value to be wrapped in a `Failure` object.

    Returns:
        A new `Failure` instance containing the given value.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> r.construct_failure(42)
        ('failure', 42)
    """
    return "failure", value


def construct_success(value: _S) -> Success[_S]:
    """Create a `Success` object from a value.

    Args:
        value: Value to be wrapped in a `Success` object.

    Returns:
        A new `Success` instance containing the given value.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> r.construct_success(42)
        ('success', 42)
    """
    return "success", value


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1]]:
    """Create function that maps `Failure` values to `Failure` values.

    `Success` values are left unchanged.

    Args:
        f: Function to apply to the `Failure` values.

    Returns:
        Maps `Failure` values to new `Failure` values
        according to the given function and
        leaves `Success` values unchanged.

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
    """Create function that maps `Failure` values to `Failure` and `Success` values.

    `Success` values are left unchanged.

    Args:
        f: Function to apply to the `Failure` values.

    Returns:
        Maps `Failure` values to `Failure` and `Success` values
        according to the given function and
        leaves `Success` values unchanged.

    Example:
        >>> from trcks.fp.monads import result as r
        >>> replace_not_found_by_default_value = r.map_failure_to_result(
        ...     lambda s: ("success", 0) if s == "not found" else ("failure", s)
        ... )
        >>> replace_not_found_by_default_value(("failure", "not found"))
        ('success', 0)
        >>> replace_not_found_by_default_value(("failure", "other failure"))
        ('failure', 'other failure')
        >>> replace_not_found_by_default_value(("success", 25.0))
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
    """Create function that maps `Success` values to `Success` values.

    `Failure` values are left unchanged.

    Args:
        f: Function to apply to the `Success` value.

    Returns:
        Leaves `Failure` values unchanged and
        maps `Success` values to new `Success` values according to the given function.

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
    """Create function that maps `Success` values to `Failure` and `Success` values.

    `Failure` values are left unchanged.

    Args:
        f: Function to apply to the `Success` value.

    Returns:
        Leaves `Failure` values unchanged and
        maps `Success` values to `Failure` and `Success` values
        according to the given function.

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
