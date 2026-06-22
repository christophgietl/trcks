"""Monadic functions for [trcks.ResultTuple][].

Provides utilities for functional composition of
functions returning [trcks.ResultTuple][] values.

Example:
    Map and tap each element inside a success tuple:

    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result_tuple as rt
    >>> def double_integer(n: int) -> int:
    ...     return n * 2
    ...
    >>> def duplicate_integer(n: int) -> tuple[int, int]:
    ...     return n, n
    ...
    >>> def log_integer(n: int) -> None:
    ...     print(f"Received: {n}")
    ...
    >>> result_tuple = pipe(
    ...     (
    ...         rt.construct_successes_from_iterable((1, 2, 3)),
    ...         rt.map_successes(double_integer),
    ...         rt.tap_successes(log_integer),
    ...         rt.map_successes_to_iterable(duplicate_integer),
    ...     )
    ... )
    Received: 2
    Received: 4
    Received: 6
    >>> result_tuple
    ('success', (2, 2, 4, 4, 6, 6))
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, deprecated
from trcks.exceptions import TrcksTypeError
from trcks.fp.composition import compose2
from trcks.fp.monads import result as r
from trcks.fp.monads import tuple_ as t

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from trcks import Failure, Result, ResultIterable, ResultTuple, SuccessTuple

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
        >>> from trcks.fp.monads import result_tuple as rt
        >>> rt.construct_failure("not found")
        ('failure', 'not found')
    """
    return r.construct_failure(value)


def construct_from_result(rslt: Result[_F, _S]) -> ResultTuple[_F, _S]:
    """Create a [trcks.ResultTuple][] object from a [trcks.Result][].

    Args:
        rslt: The [trcks.Result][] object to be wrapped.

    Returns:
        A new [trcks.ResultTuple][] instance with the success payload
            wrapped in a homogeneous tuple.

    Example:
        >>> from trcks.fp.monads import result_tuple as rt
        >>> rt.construct_from_result(("success", 7))
        ('success', (7,))
        >>> rt.construct_from_result(("failure", "oops"))
        ('failure', 'oops')
    """
    return r.map_success(t.construct)(rslt)


def construct_successes(value: _S) -> SuccessTuple[_S]:
    """Create a [trcks.SuccessTuple][] object from a single value.

    Args:
        value: A single value.

    Returns:
        A new [trcks.SuccessTuple][] instance containing the single value.

    Example:
        >>> from trcks.fp.monads import result_tuple as rt
        >>> rt.construct_successes(42)
        ('success', (42,))
    """
    return r.construct_success(t.construct(value))


def construct_successes_from_iterable(it: Iterable[_S]) -> SuccessTuple[_S]:
    """Create a [trcks.SuccessTuple][] object from an iterable.

    Args:
        it: The iterable to create
            the [trcks.SuccessTuple][] from.

    Returns:
        The [trcks.SuccessTuple][] created from the iterable.

    Example:
        >>> from trcks.fp.monads import result_tuple as rt
        >>> rt.construct_successes_from_iterable((1, 2))
        ('success', (1, 2))
    """
    return r.construct_success(tuple(it))


@deprecated("Use construct_successes_from_iterable instead")
def construct_successes_from_tuple(tpl: tuple[_S, ...]) -> SuccessTuple[_S]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.construct_successes_from_iterable][].
    """
    return construct_successes_from_iterable(tpl)  # pragma: no cover


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F2, _S1]]:
    """Create function that maps [trcks.Failure][] values to [trcks.Failure][] values.

    [trcks.SuccessTuple][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.Failure][] values
            according to the given function and
            leaves [trcks.SuccessTuple][] values unchanged.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _add_prefix(description: str) -> str:
        ...     return f"err: {description}"
        ...
        >>> add_prefix: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_failure(_add_prefix)
        >>> add_prefix(("failure", "not found"))
        ('failure', 'err: not found')
        >>> add_prefix(("success", (1, 2)))
        ('success', (1, 2))
    """
    return r.map_failure(f)


def map_failure_to_iterable(
    f: Callable[[_F1], Iterable[_S2]],
) -> Callable[[ResultTuple[_F1, _S1]], SuccessTuple[_S1] | SuccessTuple[_S2]]:
    """Create function that maps [trcks.Failure][] values
    to homogeneous [tuple][]s.

    [trcks.SuccessTuple][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to homogeneous [tuple][]s wrapped
            in a [trcks.Success][] according to the given function and
            leaves [trcks.SuccessTuple][] values unchanged.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple, SuccessTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _recover_from_not_found(description: str) -> tuple[int, ...]:
        ...     if description == "not found":
        ...         return (0,)
        ...     return ()
        ...
        >>> recover_from_not_found: Callable[
        ...     [ResultTuple[str, int]], SuccessTuple[int]
        ... ] = rt.map_failure_to_iterable(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', (0,))
        >>> recover_from_not_found(("failure", "not authorized"))
        ('success', ())
        >>> recover_from_not_found(("success", (1, 2)))
        ('success', (1, 2))
    """

    def mapped_f(
        r_tpl: ResultTuple[_F1, _S1],
    ) -> SuccessTuple[_S1] | SuccessTuple[_S2]:
        match r_tpl:
            case ("failure", value):
                return "success", tuple(f(value))  # pyrefly: ignore[bad-argument-type]
            case ("success", _):
                return r_tpl
            case _:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_tpl, "ResultTuple"
                )

    return mapped_f


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], Result[_F2, tuple[_S1, ...] | tuple[_S2, ...]]]:
    """Create function that maps [trcks.Failure][] values
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.SuccessTuple][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.Failure][] and [trcks.Success][]
            values according to the given function and
            leaves [trcks.SuccessTuple][] values unchanged.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _recover_from_not_found(description: str) -> Result[str, int]:
        ...     if description == "not found":
        ...         return "success", 0
        ...     return "failure", description
        ...
        >>> recover_from_not_found: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_failure_to_result(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', (0,))
        >>> recover_from_not_found(("failure", "not authorized"))
        ('failure', 'not authorized')
        >>> recover_from_not_found(("success", (1, 2)))
        ('success', (1, 2))
    """
    return map_failure_to_result_iterable(compose2((f, construct_from_result)))


def map_failure_to_result_iterable(
    f: Callable[[_F1], ResultIterable[_F2, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], Result[_F2, tuple[_S1, ...] | tuple[_S2, ...]]]:
    """Create function that maps [trcks.Failure][] values
    to new [trcks.ResultTuple][] values.

    [trcks.SuccessTuple][] values are left unchanged.

    Args:
        f: Function to apply to the [trcks.Failure][] values.

    Returns:
        Maps [trcks.Failure][] values to new [trcks.ResultTuple][] values
            according to the given function and
            leaves [trcks.SuccessTuple][] values unchanged.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _recover_from_not_found(description: str) -> ResultTuple[str, int]:
        ...     if description == "not found":
        ...         return "success", (0,)
        ...     return "failure", description
        ...
        >>> recover_from_not_found: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_failure_to_result_iterable(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', (0,))
        >>> recover_from_not_found(("failure", "not authorized"))
        ('failure', 'not authorized')
        >>> recover_from_not_found(("success", (1, 2)))
        ('success', (1, 2))
    """
    return r.map_failure_to_result(compose2((f, r.map_success(tuple))))  # ty: ignore[invalid-argument-type]


@deprecated("Use map_failure_to_result_iterable instead")
def map_failure_to_result_tuple(
    f: Callable[[_F1], ResultTuple[_F2, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], Result[_F2, tuple[_S1, ...] | tuple[_S2, ...]]]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.map_failure_to_result_iterable][].
    """
    return map_failure_to_result_iterable(f)  # pragma: no cover


@deprecated("Use map_failure_to_iterable instead")
def map_failure_to_tuple(
    f: Callable[[_F1], tuple[_S2, ...]],
) -> Callable[[ResultTuple[_F1, _S1]], SuccessTuple[_S1] | SuccessTuple[_S2]]:
    """Deprecated alias for [trcks.fp.monads.result_tuple.map_failure_to_iterable][]."""
    return map_failure_to_iterable(f)  # pragma: no cover


def map_successes(
    f: Callable[[_S1], _S2],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S2]]:
    """Create function that maps each element of a [trcks.SuccessTuple][]
    to a new element.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps each element of a [trcks.SuccessTuple][] to a new element
            according to the given function.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> double_integers: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_successes(_double_integer)
        >>> double_integers(("success", (1, 2, 3)))
        ('success', (2, 4, 6))
        >>> double_integers(("failure", "not found"))
        ('failure', 'not found')
    """
    return r.map_success(t.map_(f))


def map_successes_to_iterable(
    f: Callable[[_S1], Iterable[_S2]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S2]]:
    """Create function that maps each element of a [trcks.SuccessTuple][]
    to a [collections.abc.Iterable][].

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            flat-maps each element of a [trcks.SuccessTuple][] to a
            [collections.abc.Iterable][] according to the given function.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _duplicate_integer(n: int) -> tuple[int, int]:
        ...     return n, n
        ...
        >>> duplicate_integers: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_successes_to_iterable(_duplicate_integer)
        >>> duplicate_integers(("success", (1, 2)))
        ('success', (1, 1, 2, 2))
        >>> duplicate_integers(("failure", "not found"))
        ('failure', 'not found')
    """
    return r.map_success(t.map_to_iterable(f))


def map_successes_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps each element of a [trcks.SuccessTuple][]
    to [trcks.Failure][] and [trcks.Success][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps each element of a [trcks.SuccessTuple][] to
            [trcks.Failure][] and [trcks.Success][] values according to the given
            function, returning the first [trcks.Failure][] encountered, if any.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import Result, ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _double_if_positive(n: int) -> Result[str, int]:
        ...     if n > 0:
        ...         return "success", n * 2
        ...     return "failure", "not positive"
        ...
        >>> double_if_positive: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_successes_to_result(_double_if_positive)
        >>> double_if_positive(("success", (1, 2)))
        ('success', (2, 4))
        >>> double_if_positive(("success", (1, -1, 2)))
        ('failure', 'not positive')
        >>> double_if_positive(("failure", "oops"))
        ('failure', 'oops')
    """
    return map_successes_to_result_iterable(compose2((f, construct_from_result)))


def map_successes_to_result_iterable(
    f: Callable[[_S1], ResultIterable[_F2, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1 | _F2, _S2]]:
    """Create function that maps each element of a [trcks.SuccessTuple][]
    to new [trcks.ResultTuple][] values.

    [trcks.Failure][] values are left unchanged.

    Args:
        f: Function to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Leaves [trcks.Failure][] values unchanged and
            maps each element of a [trcks.SuccessTuple][] to new
            [trcks.ResultTuple][] values according to the given function,
            returning the first [trcks.Failure][] returned by `f`, if any.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _duplicate_if_positive(n: int) -> ResultTuple[str, int]:
        ...     if n > 0:
        ...         return "success", (n, n)
        ...     return "failure", "not positive"
        ...
        >>> duplicate_if_positive: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.map_successes_to_result_iterable(_duplicate_if_positive)
        >>> duplicate_if_positive(("success", (1, 2)))
        ('success', (1, 1, 2, 2))
        >>> duplicate_if_positive(("success", (1, -1, 2)))
        ('failure', 'not positive')
        >>> duplicate_if_positive(("failure", "oops"))
        ('failure', 'oops')
    """

    def partially_mapped_f(s1s: tuple[_S1, ...]) -> ResultTuple[_F2, _S2]:
        s2s: list[_S2] = []
        for s1 in s1s:
            match f(s1):
                case ("failure", _) as r_tpl:
                    return r_tpl
                case ("success", additional_s2s):
                    s2s.extend(additional_s2s)  # pyrefly: ignore[bad-argument-type]
                case _ as r_tpl:  # pragma: no cover
                    raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                        r_tpl, "ResultIterable"
                    )
        return "success", tuple(s2s)

    def mapped_f(r_tpl: ResultTuple[_F1, _S1]) -> ResultTuple[_F1 | _F2, _S2]:
        match r_tpl:
            case ("failure", _):
                return r_tpl  # ty: ignore[invalid-return-type]
            case ("success", s1s):
                return partially_mapped_f(s1s)  # pyrefly: ignore[bad-argument-type]
            case _:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_tpl, "ResultTuple"
                )

    return mapped_f


@deprecated("Use map_successes_to_result_iterable instead")
def map_successes_to_result_tuple(
    f: Callable[[_S1], ResultTuple[_F2, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1 | _F2, _S2]]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.map_successes_to_result_iterable][].
    """
    return map_successes_to_result_iterable(f)  # pragma: no cover


@deprecated("Use map_successes_to_iterable instead")
def map_successes_to_tuple(
    f: Callable[[_S1], tuple[_S2, ...]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S2]]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.map_successes_to_iterable][].
    """
    return map_successes_to_iterable(f)  # pragma: no cover


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S1]]:
    """Create function that applies a side effect to [trcks.Failure][] values.

    [trcks.SuccessTuple][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and
            returns the original [trcks.Failure][] value.
            Passes on [trcks.SuccessTuple][] values without side effects.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _log_error(description: str) -> None:
        ...     print(f"Error: {description}")
        ...
        >>> log_error: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.tap_failure(_log_error)
        >>> log_error(("failure", "oops"))
        Error: oops
        ('failure', 'oops')
        >>> log_error(("success", (1,)))
        ('success', (1,))
    """
    return r.tap_failure(f)


def tap_failure_to_iterable(
    f: Callable[[_F1], Iterable[object]],
) -> Callable[[ResultTuple[_F1, _S1]], SuccessTuple[_F1] | SuccessTuple[_S1]]:
    """Create function that applies a [collections.abc.Iterable][]-returning
    side effect to [trcks.Failure][] values.

    [trcks.SuccessTuple][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values and converts them
            to [trcks.SuccessTuple][] values containing the original failure
            repeated once per element in the [collections.abc.Iterable][] returned
            by the side effect.
            Passes on [trcks.SuccessTuple][] values without side effects.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple, SuccessTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _log_and_alert(description: str) -> tuple[None, None]:
        ...     return (
        ...         print(f"Error logged: {description}"),
        ...         print(f"Alert sent: {description}"),
        ...     )
        ...
        >>> log_and_alert: Callable[
        ...     [ResultTuple[str, int]],
        ...     SuccessTuple[str] | SuccessTuple[int],
        ... ] = rt.tap_failure_to_iterable(_log_and_alert)
        >>> log_and_alert(("failure", "critical"))
        Error logged: critical
        Alert sent: critical
        ('success', ('critical', 'critical'))
        >>> log_and_alert(("success", (1, 2)))
        ('success', (1, 2))
    """

    def tapped_f(f1: _F1) -> tuple[_F1, ...]:
        return tuple(f1 for _s2 in f(f1))

    return map_failure_to_iterable(tapped_f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], Result[_F1, tuple[_S1, ...] | tuple[_S2, ...]]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to [trcks.Failure][] values.

    [trcks.SuccessTuple][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned (wrapped as a homogeneous tuple).
            Passes on [trcks.SuccessTuple][] values without side effects.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import Result, ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _recover_from_not_found(description: str) -> Result[None, int]:
        ...     if description == "not found":
        ...         return "success", 42
        ...     return "failure", None
        >>> recover_from_not_found: Callable[
        ...     [ResultTuple[str, int]], Result[str, tuple[int, ...]]
        ... ] = rt.tap_failure_to_result(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', (42,))
        >>> recover_from_not_found(("failure", "fatal"))
        ('failure', 'fatal')
        >>> recover_from_not_found(("success", (1, 2)))
        ('success', (1, 2))
    """
    composed_f: Callable[[_F1], ResultTuple[object, _S2]] = compose2(
        (f, construct_from_result)
    )
    return tap_failure_to_result_iterable(composed_f)


def tap_failure_to_result_iterable(
    f: Callable[[_F1], ResultIterable[object, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], Result[_F1, tuple[_S1, ...] | tuple[_S2, ...]]]:
    """Create function that applies a side effect with return type
    [trcks.ResultIterable][] to [trcks.Failure][] values.

    [trcks.SuccessTuple][] values are passed on without side effects.

    Args:
        f: Side effect to apply to the [trcks.Failure][] value.

    Returns:
        Applies the given side effect to [trcks.Failure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][]
            *this* [trcks.SuccessIterable][] is returned.
            Passes on [trcks.SuccessTuple][] values without side effects.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import Result, ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _recover_from_not_found(description: str) -> ResultTuple[None, int]:
        ...     if description == "not found":
        ...         return "success", (42,)
        ...     return "failure", None
        >>> recover_from_not_found: Callable[
        ...     [ResultTuple[str, int]], Result[str, tuple[int, ...]]
        ... ] = rt.tap_failure_to_result_iterable(_recover_from_not_found)
        >>> recover_from_not_found(("failure", "not found"))
        ('success', (42,))
        >>> recover_from_not_found(("failure", "fatal"))
        ('failure', 'fatal')
        >>> recover_from_not_found(("success", (1, 2)))
        ('success', (1, 2))
    """
    return r.tap_failure_to_result(compose2((f, r.map_success(tuple))))  # ty: ignore[invalid-argument-type]


@deprecated("Use tap_failure_to_result_iterable instead")
def tap_failure_to_result_tuple(
    f: Callable[[_F1], ResultTuple[object, _S2]],
) -> Callable[[ResultTuple[_F1, _S1]], Result[_F1, tuple[_S1, ...] | tuple[_S2, ...]]]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.tap_failure_to_result_iterable][].
    """
    return tap_failure_to_result_iterable(f)  # pragma: no cover


@deprecated("Use tap_failure_to_iterable instead")
def tap_failure_to_tuple(
    f: Callable[[_F1], tuple[object, ...]],
) -> Callable[[ResultTuple[_F1, _S1]], SuccessTuple[_F1] | SuccessTuple[_S1]]:
    """Deprecated alias for [trcks.fp.monads.result_tuple.tap_failure_to_iterable][]."""
    return tap_failure_to_iterable(
        f  # ty: ignore[invalid-argument-type]
    )  # pragma: no cover


def tap_successes(
    f: Callable[[_S1], object],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S1]]:
    """Create function that applies a side effect to each element
    of a [trcks.SuccessTuple][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessTuple][] and returns the original
            [trcks.SuccessTuple][].

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _log_integer(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> log_integers: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.tap_successes(_log_integer)
        >>> r_tpl_1 = log_integers(("success", (1, 2)))
        Received: 1
        Received: 2
        >>> r_tpl_1
        ('success', (1, 2))
        >>> r_tpl_2 = log_integers(("failure", "oops"))
        >>> r_tpl_2
        ('failure', 'oops')
    """
    return r.map_success(t.tap(f))


def tap_successes_to_iterable(
    f: Callable[[_S1], Iterable[object]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S1]]:
    """Create function that applies a [collections.abc.Iterable][]-returning
    side effect to each element of a [trcks.SuccessTuple][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessTuple][]
            and repeats each original element once per element in the
            [collections.abc.Iterable][] returned by the side effect.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _log_twice(n: int) -> tuple[None, None]:
        ...     return print(f"Received: {n}"), print(f"Received: {n}")
        ...
        >>> log_twice: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.tap_successes_to_iterable(_log_twice)
        >>> log_twice(("success", (7,)))
        Received: 7
        Received: 7
        ('success', (7, 7))
    """
    return r.map_success(t.tap_to_iterable(f))


def tap_successes_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type [trcks.Result][]
    to each element of a [trcks.SuccessTuple][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessTuple][].
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.SuccessTuple][] element is returned.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import Result, ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _validate_positive(n: int) -> Result[str, None]:
        ...     if n > 0:
        ...         return "success", None
        ...     return "failure", "not positive"
        ...
        >>> validate_positive: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.tap_successes_to_result(_validate_positive)
        >>> validate_positive(("success", (1, 2)))
        ('success', (1, 2))
        >>> validate_positive(("success", (1, -1, 2)))
        ('failure', 'not positive')
        >>> validate_positive(("failure", "oops"))
        ('failure', 'oops')
    """
    composed_f: Callable[[_S1], ResultTuple[_F2, object]] = compose2(
        (f, construct_from_result)
    )
    return tap_successes_to_result_iterable(composed_f)


def tap_successes_to_result_iterable(
    f: Callable[[_S1], ResultIterable[_F2, object]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1 | _F2, _S1]]:
    """Create function that applies a side effect with return type
    [trcks.ResultTuple][] to each element of a [trcks.SuccessTuple][].

    [trcks.Failure][] values are passed on without side effects.

    Args:
        f: Side effect to apply to each element of the [trcks.SuccessTuple][].

    Returns:
        Passes on [trcks.Failure][] values without side effects.
            Applies the given side effect to each element of the
            [trcks.SuccessTuple][].
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.SuccessIterable][],
            *the original* [trcks.SuccessTuple][] element is repeated once
            per element in the side effect output.

    Example:
        >>> from collections.abc import Callable
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import result_tuple as rt
        >>> def _validate_positive_twice(n: int) -> ResultTuple[str, None]:
        ...     if n > 0:
        ...         return "success", (None, None)
        ...     return "failure", "not positive"
        ...
        >>> validate_positive_twice: Callable[
        ...     [ResultTuple[str, int]], ResultTuple[str, int]
        ... ] = rt.tap_successes_to_result_iterable(_validate_positive_twice)
        >>> validate_positive_twice(("success", (7,)))
        ('success', (7, 7))
        >>> validate_positive_twice(("success", (1, -1)))
        ('failure', 'not positive')
    """

    def tapped_f(s1: _S1) -> ResultTuple[_F2, _S1]:
        match f(s1):
            case ("failure", _) as r_tpl:
                return r_tpl
            case ("success", s2s):
                return "success", tuple(s1 for _ in s2s)  # pyrefly: ignore[not-iterable]
            case _ as r_tpl:  # pragma: no cover
                raise TrcksTypeError.construct_from_offending_object(  # pyright: ignore[reportUnreachable]
                    r_tpl, "ResultIterable"
                )

    return map_successes_to_result_iterable(tapped_f)


@deprecated("Use tap_successes_to_result_iterable instead")
def tap_successes_to_result_tuple(
    f: Callable[[_S1], ResultTuple[_F2, object]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1 | _F2, _S1]]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.tap_successes_to_result_iterable][].
    """
    return tap_successes_to_result_iterable(f)  # pragma: no cover


@deprecated("Use tap_successes_to_iterable instead")
def tap_successes_to_tuple(
    f: Callable[[_S1], tuple[object, ...]],
) -> Callable[[ResultTuple[_F1, _S1]], ResultTuple[_F1, _S1]]:
    """Deprecated alias for
    [trcks.fp.monads.result_tuple.tap_successes_to_iterable][].
    """
    return tap_successes_to_iterable(f)  # pragma: no cover
