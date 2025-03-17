"""Higher order functions for composition."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, Union

from trcks._typing import TypeAlias, assert_never

__docformat__ = "google"


_X0 = TypeVar("_X0")
_X1 = TypeVar("_X1")
_X2 = TypeVar("_X2")
_X3 = TypeVar("_X3")
_X4 = TypeVar("_X4")
_X5 = TypeVar("_X5")
_X6 = TypeVar("_X6")
_X7 = TypeVar("_X7")
_XR = TypeVar("_XR")

# Tuple type unpacking does not work correctly in Python 3.9 and 3.10
# (see https://github.com/python/typing_extensions/issues/103).
# Therefore, the following tuple type definitions contain a lot of repetitions:

Composable1: TypeAlias = tuple[Callable[[_X0], _X1],]
Composable2: TypeAlias = tuple[
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
]
Composable3: TypeAlias = tuple[
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
]
Composable4: TypeAlias = tuple[
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
]
Composable5: TypeAlias = tuple[
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
    Callable[[_X4], _X5],
]
Composable6: TypeAlias = tuple[
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
    Callable[[_X4], _X5],
    Callable[[_X5], _X6],
]
Composable7: TypeAlias = tuple[
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
    Callable[[_X4], _X5],
    Callable[[_X5], _X6],
    Callable[[_X6], _X7],
]
Composable: TypeAlias = Union[
    Composable7[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR],
    Composable6[_X0, _X1, _X2, _X3, _X4, _X5, _XR],
    Composable5[_X0, _X1, _X2, _X3, _X4, _XR],
    Composable4[_X0, _X1, _X2, _X3, _XR],
    Composable3[_X0, _X1, _X2, _XR],
    Composable2[_X0, _X1, _XR],
    Composable1[_X0, _XR],
]

Pipeline0: TypeAlias = tuple[_X0,]
Pipeline1: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
]
Pipeline2: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
]
Pipeline3: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
]
Pipeline4: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
]
Pipeline5: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
    Callable[[_X4], _X5],
]
Pipeline6: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
    Callable[[_X4], _X5],
    Callable[[_X5], _X6],
]
Pipeline7: TypeAlias = tuple[
    _X0,
    Callable[[_X0], _X1],
    Callable[[_X1], _X2],
    Callable[[_X2], _X3],
    Callable[[_X3], _X4],
    Callable[[_X4], _X5],
    Callable[[_X5], _X6],
    Callable[[_X6], _X7],
]
Pipeline: TypeAlias = Union[
    Pipeline7[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR],
    Pipeline6[_X0, _X1, _X2, _X3, _X4, _X5, _XR],
    Pipeline5[_X0, _X1, _X2, _X3, _X4, _XR],
    Pipeline4[_X0, _X1, _X2, _X3, _XR],
    Pipeline3[_X0, _X1, _X2, _XR],
    Pipeline2[_X0, _X1, _XR],
    Pipeline1[_X0, _XR],
    Pipeline0[_XR],
]


def _concatenate(  # noqa: PLR0911
    x0: _X0, c: Composable[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR]
) -> Pipeline[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR]:
    # The following if-statements help static type checkers understand
    # that (x0, *c) has type Pipeline[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR]:
    if len(c) == 1:
        return x0, *c
    if len(c) == 2:  # noqa: PLR2004
        return x0, *c
    if len(c) == 3:  # noqa: PLR2004
        return x0, *c
    if len(c) == 4:  # noqa: PLR2004
        return x0, *c
    if len(c) == 5:  # noqa: PLR2004
        return x0, *c
    if len(c) == 6:  # noqa: PLR2004
        return x0, *c
    if len(c) == 7:  # noqa: PLR2004
        return x0, *c
    return assert_never(c)  # type: ignore [unreachable]  # pragma: no cover


def compose(
    c: Composable[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR],
) -> Callable[[_X0], _XR]:
    return lambda x0: pipe(_concatenate(x0, c))


def pipe(p: Pipeline[_X0, _X1, _X2, _X3, _X4, _X5, _X6, _XR]) -> _XR:  # noqa: PLR0911
    if len(p) == 1:
        return p[0]
    if len(p) == 2:  # noqa: PLR2004
        return p[1](p[0])
    if len(p) == 3:  # noqa: PLR2004
        return p[2](p[1](p[0]))
    if len(p) == 4:  # noqa: PLR2004
        return p[3](p[2](p[1](p[0])))
    if len(p) == 5:  # noqa: PLR2004
        return p[4](p[3](p[2](p[1](p[0]))))
    if len(p) == 6:  # noqa: PLR2004
        return p[5](p[4](p[3](p[2](p[1](p[0])))))
    if len(p) == 7:  # noqa: PLR2004
        return p[6](p[5](p[4](p[3](p[2](p[1](p[0]))))))
    if len(p) == 8:  # noqa: PLR2004
        return p[7](p[6](p[5](p[4](p[3](p[2](p[1](p[0])))))))
    return assert_never(p)  # type: ignore [unreachable]  # pragma: no cover
