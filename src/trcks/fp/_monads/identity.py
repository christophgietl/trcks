from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

__docformat__ = "google"

_P = ParamSpec("_P")
_T = TypeVar("_T")


def tap(
    callable_: Callable[Concatenate[_T, _P], object],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T], _T]:
    """Turn synchronous function into a function that returns its input.

    Args:
        callable_:
            The synchronous function to be transformed into
            a function that returns its input.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        The given function transformed into a function that returns its input.

    Examples:
        >>> from collections.abc import Callable
        >>> from trcks.fp.monads import identity as i
        >>> log_and_pass_on: Callable[[object], object] = i.tap(
        ...     lambda o: print(f"Received object {o}.")
        ... )
        >>> output = log_and_pass_on(42)
        Received object 42.
        >>> output
        42
    """

    def bypassed_callable(value: _T) -> _T:
        _ = callable_(value, *args, **kwargs)
        return value

    return bypassed_callable
