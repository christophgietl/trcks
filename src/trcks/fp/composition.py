"""Types and higher order functions for function composition.

Example:
    Sequentially apply two functions to one input value
    in three different ways:

    >>> def to_length_string(n: int) -> str:
    ...     return f"Length: {n}"
    ...
    >>> input_ = "Hello, world!"
    >>> to_length_string(len(input_))
    'Length: 13'
    >>> get_length_string = compose((len, to_length_string))
    >>> get_length_string(input_)
    'Length: 13'
    >>> pipe((input_, len, to_length_string))
    'Length: 13'
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

from trcks._typing import TypeVar, assert_never

__docformat__ = "google"


_IN = TypeVar("_IN")
_OUT = TypeVar("_OUT")
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

Composable1: TypeAlias = tuple[Callable[[_T0], _T1],]
"""A single function."""

Composable2: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
]
"""Two compatible functions that can be applied sequentially from first to last."""

Composable3: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
]
"""Three compatible functions that can be applied sequentially from first to last."""

Composable4: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
]
"""Four compatible functions that can be applied sequentially from first to last."""

Composable5: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
]
"""Five compatible functions that can be applied sequentially from first to last."""

Composable6: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
]
"""Six compatible functions that can be applied sequentially from first to last."""

Composable7: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
    Callable[[_T6], _T7],
]
"""Seven compatible functions that can be applied sequentially from first to last."""

Composable: TypeAlias = (
    Composable7[_IN, _T1, _T2, _T3, _T4, _T5, _T6, _OUT]
    | Composable6[_IN, _T1, _T2, _T3, _T4, _T5, _OUT]
    | Composable5[_IN, _T1, _T2, _T3, _T4, _OUT]
    | Composable4[_IN, _T1, _T2, _T3, _OUT]
    | Composable3[_IN, _T1, _T2, _OUT]
    | Composable2[_IN, _T1, _OUT]
    | Composable1[_IN, _OUT]
)
"""Up to seven compatible functions
that can be applied sequentially from first to last."""

Pipeline0: TypeAlias = tuple[_T0,]
"""A single value."""

Pipeline1: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
]
"""A single value followed by a single compatible function that can be applied."""

Pipeline2: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
]
"""A single value followed by two compatible functions
that can be applied sequentially from first to last."""

Pipeline3: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
]
"""A single value followed by three compatible functions
that can be applied sequentially from first to last."""

Pipeline4: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
]
"""A single value followed by four compatible functions
that can be applied sequentially from first to last."""

Pipeline5: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
]
"""A single value followed by five compatible functions
that can be applied sequentially from first to last."""

Pipeline6: TypeAlias = tuple[
    _T0,
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
]
"""A single value followed by six compatible functions
that can be applied sequentially from first to last."""

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
"""A single value followed by seven compatible functions
that can be applied sequentially from first to last."""

Pipeline: TypeAlias = (
    Pipeline7[_T0, _T1, _T2, _T3, _T4, _T5, _T6, _OUT]
    | Pipeline6[_T0, _T1, _T2, _T3, _T4, _T5, _OUT]
    | Pipeline5[_T0, _T1, _T2, _T3, _T4, _OUT]
    | Pipeline4[_T0, _T1, _T2, _T3, _OUT]
    | Pipeline3[_T0, _T1, _T2, _OUT]
    | Pipeline2[_T0, _T1, _OUT]
    | Pipeline1[_T0, _OUT]
    | Pipeline0[_OUT]
)
"""A single value followed by up to seven compatible functions
that can be applied sequentially from first to last."""


def compose1(c: Composable1[_T0, _T1]) -> Callable[[_T0], _T1]:
    """Compose a single function.

    Args:
        c: A single function.

    Returns:
        Function that applies the given function.

    Example:
        >>> get_length = compose1((len,))
        >>> get_length("Hello, world!")
        13
    """
    return lambda t0: c[0](t0)


def compose2(c: Composable2[_T0, _T1, _T2]) -> Callable[[_T0], _T2]:
    """Compose two compatible functions from first to last.

    Args:
        c: Two compatible functions that can be applied sequentially from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> get_length_string = compose2((len, lambda n: f"Length: {n}"))
        >>> get_length_string("Hello, world!")
        'Length: 13'
    """
    return lambda t0: c[1](c[0](t0))


def compose3(c: Composable3[_T0, _T1, _T2, _T3]) -> Callable[[_T0], _T3]:
    """Compose three compatible functions from first to last.

    Args:
        c:
            Three compatible functions that can be applied sequentially
            from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> add_one = lambda n: n + 1
        >>> square = lambda n: n * n
        >>> to_string = lambda n: f"Result: {n}"
        >>> compute = compose3((add_one, square, to_string))
        >>> compute(3)
        'Result: 16'
    """
    return lambda t0: c[2](c[1](c[0](t0)))


def compose4(c: Composable4[_T0, _T1, _T2, _T3, _T4]) -> Callable[[_T0], _T4]:
    """Compose four compatible functions from first to last.

    Args:
        c:
            Four compatible functions that can be applied sequentially
            from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> add_one = lambda n: n + 1
        >>> square = lambda n: n * n
        >>> halve = lambda n: n / 2
        >>> to_string = lambda n: f"Result: {n}"
        >>> compute = compose4((add_one, square, halve, to_string))
        >>> compute(3)
        'Result: 8.0'
    """
    return lambda t0: c[3](c[2](c[1](c[0](t0))))


def compose5(c: Composable5[_T0, _T1, _T2, _T3, _T4, _T5]) -> Callable[[_T0], _T5]:
    """Compose five compatible functions from first to last.

    Args:
        c:
            Five compatible functions that can be applied sequentially
            from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> add_one = lambda n: n + 1
        >>> square = lambda n: n * n
        >>> halve = lambda n: n / 2
        >>> to_string = lambda n: f"Result: {n}"
        >>> exclaim = lambda s: s + "!"
        >>> compute = compose5((add_one, square, halve, to_string, exclaim))
        >>> compute(3)
        'Result: 8.0!'
    """
    return lambda t0: c[4](c[3](c[2](c[1](c[0](t0)))))


def compose6(c: Composable6[_T0, _T1, _T2, _T3, _T4, _T5, _T6]) -> Callable[[_T0], _T6]:
    """Compose six compatible functions from first to last.

    Args:
        c: Six compatible functions that can be applied sequentially from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> add_one = lambda n: n + 1
        >>> square = lambda n: n * n
        >>> halve = lambda n: n / 2
        >>> to_string = lambda n: f"Result: {n}"
        >>> exclaim = lambda s: s + "!"
        >>> to_list = lambda s: [s]
        >>> compute = compose6((add_one, square, halve, to_string, exclaim, to_list))
        >>> compute(3)
        ['Result: 8.0!']
    """
    return lambda t0: c[5](c[4](c[3](c[2](c[1](c[0](t0))))))


def compose7(
    c: Composable7[_T0, _T1, _T2, _T3, _T4, _T5, _T6, _T7],
) -> Callable[[_T0], _T7]:
    """Compose seven compatible functions from first to last.

    Args:
        c:
            Seven compatible functions that can be applied sequentially
            from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> add_one = lambda n: n + 1
        >>> square = lambda n: n * n
        >>> halve = lambda n: n / 2
        >>> to_string = lambda n: f"Result: {n}"
        >>> exclaim = lambda s: s + "!"
        >>> to_list = lambda s: [s]
        >>> wrap_in_dict = lambda lst: {"result": lst}
        >>> compute = compose7(
        ...     (add_one, square, halve, to_string, exclaim, to_list, wrap_in_dict)
        ... )
        >>> compute(3)
        {'result': ['Result: 8.0!']}
    """
    return lambda t0: c[6](c[5](c[4](c[3](c[2](c[1](c[0](t0)))))))


def compose(  # noqa: PLR0911
    c: Composable[_IN, _T1, _T2, _T3, _T4, _T5, _T6, _OUT],
) -> Callable[[_IN], _OUT]:
    """Compose a tuple of compatible functions from first to last.

    Args:
        c: Compatible functions that can be applied sequentially from first to last.

    Returns:
        Function that applies the given functions from first to last.

    Example:
        >>> get_length_string = compose((len, lambda n: f"Length: {n}"))
        >>> get_length_string("Hello, world!")
        'Length: 13'
    """
    if len(c) == 1:
        return compose1(c)
    if len(c) == 2:  # noqa: PLR2004
        return compose2(c)
    if len(c) == 3:  # noqa: PLR2004
        return compose3(c)
    if len(c) == 4:  # noqa: PLR2004
        return compose4(c)
    if len(c) == 5:  # noqa: PLR2004
        return compose5(c)
    if len(c) == 6:  # noqa: PLR2004
        return compose6(c)
    if len(c) == 7:  # noqa: PLR2004
        return compose7(c)
    return assert_never(c)  # type: ignore [unreachable]  # pragma: no cover


def pipe(p: Pipeline[_T0, _T1, _T2, _T3, _T4, _T5, _T6, _OUT]) -> _OUT:
    """Evaluate a `Pipeline`.

    Args:
        p:
            Single value followed by up to seven compatible functions
            that can be applied sequentially from first to last.

    Returns:
        Result of sequentially applying the given functions from first to last
            to the given value.

    Example:
        >>> pipe(("Hello, world!", len, lambda n: f"Length: {n}"))
        'Length: 13'
    """
    if len(p) == 1:
        return p[0]
    return compose(p[1:])(p[0])
