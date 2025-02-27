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

_T = TypeVar("_T")
_T0 = TypeVar("_T0")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_T5 = TypeVar("_T5")
_T6 = TypeVar("_T6")
_T7 = TypeVar("_T7")
_T8 = TypeVar("_T8")
_T9 = TypeVar("_T9")

_F: TypeAlias = Callable[[_T0], _T1]


@overload
def compose() -> _F[_T0, _T0]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    /,
) -> _F[_T0, _T1]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    /,
) -> _F[_T0, _T2]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    /,
) -> _F[_T0, _T3]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    /,
) -> _F[_T0, _T4]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    /,
) -> _F[_T0, _T5]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    /,
) -> _F[_T0, _T6]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    f7: _F[_T6, _T7],
    /,
) -> _F[_T0, _T7]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    f7: _F[_T6, _T7],
    f8: _F[_T7, _T8],
    /,
) -> _F[_T0, _T8]: ...


@overload
def compose(
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    f7: _F[_T6, _T7],
    f8: _F[_T7, _T8],
    f9: _F[_T8, _T9],
    /,
) -> _F[_T0, _T9]: ...


@overload
def compose(*fs: _F[_T, _T]) -> _F[_T, _T]: ...


def compose(*fs: _F[Any, Any]) -> _F[Any, Any]:  # type: ignore[explicit-any]
    def composed(value: Any) -> Any:  # type: ignore[explicit-any]  # noqa: ANN401
        return functools.reduce(lambda acc, f: f(acc), fs, value)

    return composed


@overload
def pipe(
    value: _T0,
    /,
) -> _T0: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    /,
) -> _T1: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    /,
) -> _T2: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    /,
) -> _T3: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    /,
) -> _T4: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    /,
) -> _T5: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    /,
) -> _T6: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    f7: _F[_T6, _T7],
    /,
) -> _T7: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    f7: _F[_T6, _T7],
    f8: _F[_T7, _T8],
    /,
) -> _T8: ...


@overload
def pipe(
    value: _T0,
    f1: _F[_T0, _T1],
    f2: _F[_T1, _T2],
    f3: _F[_T2, _T3],
    f4: _F[_T3, _T4],
    f5: _F[_T4, _T5],
    f6: _F[_T5, _T6],
    f7: _F[_T6, _T7],
    f8: _F[_T7, _T8],
    f9: _F[_T8, _T9],
    /,
) -> _T9: ...


@overload
def pipe(
    value: _T,
    *fs: _F[_T, _T],
) -> _T: ...


def pipe(value: Any, *fs: _F[Any, Any]) -> Any:  # type: ignore[explicit-any]
    return compose(*fs)(value)
