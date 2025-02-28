"""Higher order functions for composition.

This module is heavily inspired by the expression library
(see https://github.com/dbrattli/Expression/blob/a39d98592012e482df140af86b82a59c3d5ba4b7/expression/core/pipe.py).
"""

import functools
import sys
from collections.abc import Callable
from typing import Any, TypeVar, overload

if sys.version_info >= (3, 11):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_X = TypeVar("_X")
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

_Morphism: TypeAlias = Callable[[_X0], _X1]
_Endomorphism: TypeAlias = Callable[[_X], _X]


@overload
def pipe(
    value: _X0,
    /,
) -> _X0: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    /,
) -> _X1: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    /,
) -> _X2: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    /,
) -> _X3: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    /,
) -> _X4: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    /,
) -> _X5: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    /,
) -> _X6: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    f7: _Morphism[_X6, _X7],
    /,
) -> _X7: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    f7: _Morphism[_X6, _X7],
    f8: _Morphism[_X7, _X8],
    /,
) -> _X8: ...


@overload
def pipe(
    value: _X0,
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    f7: _Morphism[_X6, _X7],
    f8: _Morphism[_X7, _X8],
    f9: _Morphism[_X8, _X9],
    /,
) -> _X9: ...


@overload
def pipe(
    value: _X,
    *fs: _Endomorphism[_X],
) -> _X: ...


def pipe(value: Any, *fs: _Morphism[Any, Any]) -> Any:  # type: ignore[explicit-any]
    return functools.reduce(lambda acc, f: f(acc), fs, value)


@overload
def compose() -> _Endomorphism[_X0]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    /,
) -> _Morphism[_X0, _X1]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    /,
) -> _Morphism[_X0, _X2]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    /,
) -> _Morphism[_X0, _X3]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    /,
) -> _Morphism[_X0, _X4]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    /,
) -> _Morphism[_X0, _X5]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    /,
) -> _Morphism[_X0, _X6]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    f7: _Morphism[_X6, _X7],
    /,
) -> _Morphism[_X0, _X7]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    f7: _Morphism[_X6, _X7],
    f8: _Morphism[_X7, _X8],
    /,
) -> _Morphism[_X0, _X8]: ...


@overload
def compose(
    f1: _Morphism[_X0, _X1],
    f2: _Morphism[_X1, _X2],
    f3: _Morphism[_X2, _X3],
    f4: _Morphism[_X3, _X4],
    f5: _Morphism[_X4, _X5],
    f6: _Morphism[_X5, _X6],
    f7: _Morphism[_X6, _X7],
    f8: _Morphism[_X7, _X8],
    f9: _Morphism[_X8, _X9],
    /,
) -> _Morphism[_X0, _X9]: ...


@overload
def compose(*fs: _Endomorphism[_X]) -> _Endomorphism[_X]: ...


def compose(*fs: _Morphism[Any, Any]) -> _Morphism[Any, Any]:  # type: ignore[explicit-any]
    return lambda value: pipe(value, *fs)
