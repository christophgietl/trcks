"""Private implementation of monadic functions for [trcks.Result][]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import Never, TypeVar, assert_type
from trcks.fp._monads import identity as i
from trcks.fp.composition import compose2

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks import Failure, Result, Success


__docformat__ = "google"

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_P = ParamSpec("_P")
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
    f: Callable[Concatenate[_F1, _P], _F2], *args: _P.args, **kwargs: _P.kwargs
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1]]:
    """Create function that maps [trcks.Failure][] values to [trcks.Failure][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

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
    return map_failure_to_result(compose2((f, construct_failure)), *args, **kwargs)


def map_failure_to_result(
    f: Callable[Concatenate[_F1, _P], Result[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.Success][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

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
        match rslt:
            case ("failure", value):
                return f(value, *args, **kwargs)
            case ("success", _):
                return rslt
            case _:  # pragma: no cover
                assert_type(rslt, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(rslt).__name__!r} is not a valid Result"
                raise TypeError(msg)

    return mapped_f


def map_success(
    f: Callable[Concatenate[_S1, _P], _S2], *args: _P.args, **kwargs: _P.kwargs
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S2]]:
    """Create function that maps [trcks.Success][] values to [trcks.Success][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

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
    return map_success_to_result(compose2((f, construct_success)), *args, **kwargs)


def map_success_to_result(
    f: Callable[Concatenate[_S1, _P], Result[_F2, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], Result[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.Success][] values
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

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
        match rslt:
            case ("failure", _):
                return rslt
            case ("success", value):
                return f(value, *args, **kwargs)
            case _:  # pragma: no cover
                assert_type(rslt, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(rslt).__name__!r} is not a valid Result"
                raise TypeError(msg)

    return mapped_f


def tap_failure(
    f: Callable[Concatenate[_F1, _P], object], *args: _P.args, **kwargs: _P.kwargs
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S1]]:
    """Create function that applies a side effect to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and
            returns the original [trcks.Failure][] value.
            Passes on [trcks.Success][] values without side effects.
    """
    return map_failure(i.tap(f, *args, **kwargs))


def tap_failure_to_result(
    f: Callable[Concatenate[_F1, _P], Result[object, _S2]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S1 | _S2]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to [trcks.Failure][] values.

    [trcks.Success][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] value is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned.
            Passes on [trcks.Success][] values without side effects.
    """

    def bypassed_f(value: _F1) -> Result[_F1, _S2]:
        match f(value, *args, **kwargs):
            case ("failure", _):
                return construct_failure(value)
            case ("success", _) as rslt:
                return rslt
            case _ as rslt:  # pragma: no cover
                assert_type(rslt, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(rslt).__name__!r} is not a valid Result"
                raise TypeError(msg)

    return map_failure_to_result(bypassed_f)


def tap_success(
    f: Callable[Concatenate[_S1, _P], object], *args: _P.args, **kwargs: _P.kwargs
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S1]]:
    """Create function that applies a side effect to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values and
            returns the original [trcks.Success][] value.
    """
    return map_success(i.tap(f, *args, **kwargs))


def tap_success_to_result(
    f: Callable[Concatenate[_S1, _P], Result[_F2, object]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[Result[_F1, _S1]], Result[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to [trcks.Success][] values.

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Success][] value.
        *args:
            Positional arguments to be passed to `f`.
        **kwargs:
            Keyword arguments to be passed to `f`.

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to [trcks.Success][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.Success][] value is returned.
    """

    def bypassed_f(value: _S1) -> Result[_F2, _S1]:
        match f(value, *args, **kwargs):
            case ("failure", _) as rslt:
                return rslt
            case ("success", _):
                return construct_success(value)
            case _ as rslt:  # pragma: no cover
                assert_type(rslt, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(rslt).__name__!r} is not a valid Result"
                raise TypeError(msg)

    return map_success_to_result(bypassed_f)
