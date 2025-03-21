"""Types and higher order functions for function composition.

Attributes:
    Composable:
        Up to seven compatible functions that can be applied sequentially
        from first to last.
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
    Pipeline:
        A single value followed by up to seven compatible functions
        that can be applied sequentially from first to last.
    Pipeline0:
        A single value.
    Pipeline1:
        A single value followed by a single compatible function
        that can be applied.
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
from typing import Union

from trcks._typing import TypeAlias, TypeVar, assert_never

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

# Tuple type unpacking does not work correctly in Python 3.9 and 3.10
# (see https://github.com/python/typing_extensions/issues/103).
# Therefore, the following tuple type definitions contain a lot of repetitions:

Composable1: TypeAlias = tuple[Callable[[_T0], _T1],]

Composable2: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
]

Composable3: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
]

Composable4: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
]

Composable5: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
]

Composable6: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
]

Composable7: TypeAlias = tuple[
    Callable[[_T0], _T1],
    Callable[[_T1], _T2],
    Callable[[_T2], _T3],
    Callable[[_T3], _T4],
    Callable[[_T4], _T5],
    Callable[[_T5], _T6],
    Callable[[_T6], _T7],
]

Composable: TypeAlias = Union[
    Composable7[_IN, _T1, _T2, _T3, _T4, _T5, _T6, _OUT],
    Composable6[_IN, _T1, _T2, _T3, _T4, _T5, _OUT],
    Composable5[_IN, _T1, _T2, _T3, _T4, _OUT],
    Composable4[_IN, _T1, _T2, _T3, _OUT],
    Composable3[_IN, _T1, _T2, _OUT],
    Composable2[_IN, _T1, _OUT],
    Composable1[_IN, _OUT],
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

Pipeline: TypeAlias = Union[
    Pipeline7[_T0, _T1, _T2, _T3, _T4, _T5, _T6, _OUT],
    Pipeline6[_T0, _T1, _T2, _T3, _T4, _T5, _OUT],
    Pipeline5[_T0, _T1, _T2, _T3, _T4, _OUT],
    Pipeline4[_T0, _T1, _T2, _T3, _OUT],
    Pipeline3[_T0, _T1, _T2, _OUT],
    Pipeline2[_T0, _T1, _OUT],
    Pipeline1[_T0, _OUT],
    Pipeline0[_OUT],
]


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
        return lambda in_: c[0](in_)
    if len(c) == 2:  # noqa: PLR2004
        return lambda in_: c[1](c[0](in_))
    if len(c) == 3:  # noqa: PLR2004
        return lambda in_: c[2](c[1](c[0](in_)))
    if len(c) == 4:  # noqa: PLR2004
        return lambda in_: c[3](c[2](c[1](c[0](in_))))
    if len(c) == 5:  # noqa: PLR2004
        return lambda in_: c[4](c[3](c[2](c[1](c[0](in_)))))
    if len(c) == 6:  # noqa: PLR2004
        return lambda in_: c[5](c[4](c[3](c[2](c[1](c[0](in_))))))
    if len(c) == 7:  # noqa: PLR2004
        return lambda in_: c[6](c[5](c[4](c[3](c[2](c[1](c[0](in_)))))))
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
