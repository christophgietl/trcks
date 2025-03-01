"""Higher order functions for composition."""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional, overload

from trcks._typing_extensions import TypeAlias, TypeVar

_X0 = TypeVar("_X0")
_X1 = TypeVar("_X1")
_X2 = TypeVar("_X2")
_X3 = TypeVar("_X3")
_X4 = TypeVar("_X4")
_X5 = TypeVar("_X5")
_X6 = TypeVar("_X6")
_X7 = TypeVar("_X7")
_X8 = TypeVar("_X8")
_X9 = TypeVar("_X9")

_F: TypeAlias = Callable[[_X0], _X1]
_OF: TypeAlias = Optional[_F[_X0, _X1]]


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: None = None,
    f3: _OF[_X2, _X3] = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X1]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: None = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X2]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: None = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X3]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: None = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X4]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: None = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X5]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: None = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X6]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: _F[_X6, _X7],
    f8: None = None,
    f9: _OF[_X8, _X9] = None,
) -> _F[_X0, _X7]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: _F[_X6, _X7],
    f8: _F[_X7, _X8],
    f9: None = None,
) -> _F[_X0, _X8]: ...


@overload
def compose(
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: _F[_X6, _X7],
    f8: _F[_X7, _X8],
    f9: _F[_X8, _X9],
) -> _F[_X0, _X9]: ...


def compose(  # noqa: PLR0911, PLR0913
    f1: _F[_X0, _X1],
    f2: _OF[_X1, _X2] = None,
    f3: _OF[_X2, _X3] = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> (
    _F[_X0, _X1]
    | _F[_X0, _X2]
    | _F[_X0, _X3]
    | _F[_X0, _X4]
    | _F[_X0, _X5]
    | _F[_X0, _X6]
    | _F[_X0, _X7]
    | _F[_X0, _X8]
    | _F[_X0, _X9]
):
    if f2 is None:
        return lambda x0: f1(x0)
    if f3 is None:
        return lambda x0: f2(f1(x0))
    if f4 is None:
        return lambda x0: f3(f2(f1(x0)))
    if f5 is None:
        return lambda x0: f4(f3(f2(f1(x0))))
    if f6 is None:
        return lambda x0: f5(f4(f3(f2(f1(x0)))))
    if f7 is None:
        return lambda x0: f6(f5(f4(f3(f2(f1(x0))))))
    if f8 is None:
        return lambda x0: f7(f6(f5(f4(f3(f2(f1(x0)))))))
    if f9 is None:
        return lambda x0: f8(f7(f6(f5(f4(f3(f2(f1(x0))))))))
    return lambda x0: f9(f8(f7(f6(f5(f4(f3(f2(f1(x0)))))))))


@overload
def pipe(
    x0: _X0,
    f1: None = None,
    f2: _OF[_X1, _X2] = None,
    f3: _OF[_X2, _X3] = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X0: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: None = None,
    f3: _OF[_X2, _X3] = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X1: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: None = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X2: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: None = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X3: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: None = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X4: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: None = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X5: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: None = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X6: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: _F[_X6, _X7],
    f8: None = None,
    f9: _OF[_X8, _X9] = None,
) -> _X7: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: _F[_X6, _X7],
    f8: _F[_X7, _X8],
    f9: None = None,
) -> _X8: ...


@overload
def pipe(
    x0: _X0,
    f1: _F[_X0, _X1],
    f2: _F[_X1, _X2],
    f3: _F[_X2, _X3],
    f4: _F[_X3, _X4],
    f5: _F[_X4, _X5],
    f6: _F[_X5, _X6],
    f7: _F[_X6, _X7],
    f8: _F[_X7, _X8],
    f9: _F[_X8, _X9],
) -> _X9: ...


def pipe(  # noqa: PLR0911, PLR0913
    x0: _X0,
    f1: _OF[_X0, _X1] = None,
    f2: _OF[_X1, _X2] = None,
    f3: _OF[_X2, _X3] = None,
    f4: _OF[_X3, _X4] = None,
    f5: _OF[_X4, _X5] = None,
    f6: _OF[_X5, _X6] = None,
    f7: _OF[_X6, _X7] = None,
    f8: _OF[_X7, _X8] = None,
    f9: _OF[_X8, _X9] = None,
) -> _X0 | _X1 | _X2 | _X3 | _X4 | _X5 | _X6 | _X7 | _X8 | _X9:
    if f1 is None:
        return x0
    if f2 is None:
        return f1(x0)
    if f3 is None:
        return f2(f1(x0))
    if f4 is None:
        return f3(f2(f1(x0)))
    if f5 is None:
        return f4(f3(f2(f1(x0))))
    if f6 is None:
        return f5(f4(f3(f2(f1(x0)))))
    if f7 is None:
        return f6(f5(f4(f3(f2(f1(x0))))))
    if f8 is None:
        return f7(f6(f5(f4(f3(f2(f1(x0)))))))
    if f9 is None:
        return f8(f7(f6(f5(f4(f3(f2(f1(x0))))))))
    return f9(f8(f7(f6(f5(f4(f3(f2(f1(x0)))))))))
