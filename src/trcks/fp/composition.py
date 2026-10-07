"""Types and higher-order functions for function composition.

Attributes:
    Composable1:
        A single function.
    Composable2:
        Two compatible functions that can be applied sequentially from first to last.
    Composable3:
        Three compatible functions that can be applied sequentially from first to last.
    Composable4:
        Four compatible functions that can be applied sequentially from first to last.
    Composable5:
        Five compatible functions that can be applied sequentially from first to last.
    Composable6:
        Six compatible functions that can be applied sequentially from first to last.
    Composable7:
        Seven compatible functions that can be applied sequentially from first to last.
    Pipeline0:
        A single value.
    Pipeline1:
        A single value followed by a single compatible function that can be applied.
    Pipeline2:
        A single value followed by two compatible functions
        that can be applied sequentially from first to last.
    Pipeline3:
        A single value followed by three compatible functions
        that can be applied sequentially from first to last.
    Pipeline4:
        A single value followed by four compatible functions
        that can be applied sequentially from first to last.
    Pipeline5:
        A single value followed by five compatible functions
        that can be applied sequentially from first to last.
    Pipeline6:
        A single value followed by six compatible functions
        that can be applied sequentially from first to last.
    Pipeline7:
        A single value followed by seven compatible functions
        that can be applied sequentially from first to last.

Examples:
    Sequentially apply two compatible functions to one input value
    in three different ways:

    >>> from trcks.fp.composition import compose, pipe
    >>> def to_length_string(n: int) -> str:
    ...     return f"Length: {n}"
    ...
    >>> input_ = "Hello, world!"
    >>> to_length_string(len(input_))
    'Length: 13'
    >>> get_length_string = compose(len, to_length_string)
    >>> get_length_string(input_)
    'Length: 13'
    >>> pipe(input_, len, to_length_string)
    'Length: 13'

    The first function passed to [`compose`][trcks.fp.composition.compose]
    may accept multiple arguments:

    >>> from trcks.fp.composition import compose
    >>> def repeat(text: str, times: int = 2) -> str:
    ...     return text * times
    ...
    >>> get_repeated_length = compose(repeat, len)
    >>> get_repeated_length("Hi")
    4
    >>> get_repeated_length("Hi", 3)
    6
"""

from collections.abc import Callable
from typing import Any, ParamSpec, TypeAlias, overload

from trcks._typing import TypeVar

__docformat__ = "google"

_P0 = ParamSpec("_P0")
_T0 = TypeVar("_T0")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_T5 = TypeVar("_T5")
_T6 = TypeVar("_T6")
_T7 = TypeVar("_T7")

# Tuple type unpacking does not work correctly in Python 3.10
# (see https://github.com/python/typing_extensions/issues/103).
# Therefore, the following tuple type definitions contain a lot of repetitions:
Composable1: TypeAlias = tuple[Callable[_P0, _T1],]
Composable2: TypeAlias = tuple[
    Callable[_P0, _T1],
    Callable[[_T1], _T2],
]
Composable3: TypeAlias = tuple[
    Callable[_P0, _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
]
Composable4: TypeAlias = tuple[
    Callable[_P0, _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
]
Composable5: TypeAlias = tuple[
    Callable[_P0, _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
]
Composable6: TypeAlias = tuple[
    Callable[_P0, _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
]
Composable7: TypeAlias = tuple[
    Callable[_P0, _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
    Callable[[_T6], _T7],
]

Pipeline0: TypeAlias = tuple[_T0,]
Pipeline1: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
]
Pipeline2: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
]
Pipeline3: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
]
Pipeline4: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
]
Pipeline5: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
]
Pipeline6: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
]
Pipeline7: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
    Callable[[_T6], _T7],
]


@overload
def compose(callable1: Callable[_P0, _T1], /) -> Callable[_P0, _T1]: ...


@overload
def compose(
    callable1: Callable[_P0, _T1], callable2: Callable[[_T1], _T2], /
) -> Callable[_P0, _T2]: ...


@overload
def compose(
    callable1: Callable[_P0, _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    /,
) -> Callable[_P0, _T3]: ...


@overload
def compose(
    callable1: Callable[_P0, _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    /,
) -> Callable[_P0, _T4]: ...


@overload
def compose(
    callable1: Callable[_P0, _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    callable5: Callable[[_T4], _T5],
    /,
) -> Callable[_P0, _T5]: ...


@overload
def compose(
    callable1: Callable[_P0, _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    callable5: Callable[[_T4], _T5],
    callable6: Callable[[_T5], _T6],
    /,
) -> Callable[_P0, _T6]: ...


@overload
def compose(
    callable1: Callable[_P0, _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    callable5: Callable[[_T4], _T5],
    callable6: Callable[[_T5], _T6],
    callable7: Callable[[_T6], _T7],
    /,
) -> Callable[_P0, _T7]: ...


def compose(  # type: ignore[explicit-any]
    callable1: Callable[_P0, Any],  # pyrefly: ignore[explicit-any]
    /,
    *callables: Callable[[Any], Any],  # pyrefly: ignore[explicit-any]
) -> Callable[_P0, Any]:  # pyrefly: ignore[explicit-any]
    """Concatenate compatible functions from first to last.

    Args:
        callable1: First function.
        callables: Zero to six additional compatible functions.

    Returns:
        Function that applies the given functions from first to last.

    Examples:
        Sequentially apply two compatible functions to one input value:

        >>> from trcks.fp.composition import compose
        >>> def to_length_string(n: int) -> str:
        ...     return f"Length: {n}"
        ...
        >>> get_length_string = compose(len, to_length_string)
        >>> get_length_string("Hello, world!")
        'Length: 13'

        The first function may accept multiple arguments:

        >>> from trcks.fp.composition import compose
        >>> def repeat(text: str, times: int = 2) -> str:
        ...     return text * times
        ...
        >>> get_repeated_length = compose(repeat, len)
        >>> get_repeated_length("Hi")
        4
        >>> get_repeated_length("Hi", 3)
        6
    """

    def composed(*args: _P0.args, **kwargs: _P0.kwargs) -> Any:  # type: ignore[explicit-any]  # pyrefly: ignore[explicit-any]  # noqa: ANN401
        output = callable1(*args, **kwargs)
        for callable_ in callables:
            output = callable_(output)
        return output

    return composed


@overload
def pipe(input_: _T0, /) -> _T0: ...


@overload
def pipe(input_: _T0, callable1: Callable[[_T0], _T1], /) -> _T1: ...


@overload
def pipe(
    input_: _T0, callable1: Callable[[_T0], _T1], callable2: Callable[[_T1], _T2], /
) -> _T2: ...


@overload
def pipe(
    input_: _T0,
    callable1: Callable[[_T0], _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    /,
) -> _T3: ...


@overload
def pipe(
    input_: _T0,
    callable1: Callable[[_T0], _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    /,
) -> _T4: ...


@overload
def pipe(
    input_: _T0,
    callable1: Callable[[_T0], _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    callable5: Callable[[_T4], _T5],
    /,
) -> _T5: ...


@overload
def pipe(
    input_: _T0,
    callable1: Callable[[_T0], _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    callable5: Callable[[_T4], _T5],
    callable6: Callable[[_T5], _T6],
    /,
) -> _T6: ...


@overload
def pipe(
    input_: _T0,
    callable1: Callable[[_T0], _T1],
    callable2: Callable[[_T1], _T2],
    callable3: Callable[[_T2], _T3],
    callable4: Callable[[_T3], _T4],
    callable5: Callable[[_T4], _T5],
    callable6: Callable[[_T5], _T6],
    callable7: Callable[[_T6], _T7],
    /,
) -> _T7: ...


def pipe(input_: Any, /, *callables: Callable[[Any], Any]) -> Any:  # type: ignore[explicit-any]  # pyrefly: ignore[explicit-any]
    """Evaluate a pipeline consisting of a starting value and compatible functions.

    Args:
        input_: Starting value of the pipeline.
        callables:
            Zero to seven compatible functions
            that can be applied to `input_` sequentially from first to last.

    Returns:
        Result of sequentially applying the given functions to the starting value.

    Examples:
        Sequentially apply two compatible functions to one input value:

        >>> from trcks.fp.composition import pipe
        >>> def to_length_string(n: int) -> str:
        ...     return f"Length: {n}"
        ...
        >>> pipe("Hello, world!", len, to_length_string)
        'Length: 13'
    """
    output = input_
    for callable_ in callables:
        output = callable_(output)
    return output
