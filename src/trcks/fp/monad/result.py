from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Literal, TypeVar, Union

if TYPE_CHECKING:
    from collections.abc import Callable

if sys.version_info >= (3, 11):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")

_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)


Failure: TypeAlias = tuple[Literal["failure"], _F_co]
Success: TypeAlias = tuple[Literal["success"], _S_co]
Result: TypeAlias = Union[Failure[_F_co], Success[_S_co]]


def flat_map_failure(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1 | _S2]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1 | _S2]:
        return f(rslt[1]) if rslt[0] == "failure" else rslt

    return mapped_f


def flat_map_success(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F1 | _F2, _S2]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1 | _F2, _S2]:
        return f(rslt[1]) if rslt[0] == "success" else rslt

    return mapped_f


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1]:
        return of_failure(f(rslt[1])) if rslt[0] == "failure" else rslt

    return mapped_f


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S2]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1, _S2]:
        return of_success(f(rslt[1])) if rslt[0] == "success" else rslt

    return mapped_f


def of_failure(value: _F) -> Failure[_F]:
    return ("failure", value)


def of_success(value: _S) -> Success[_S]:
    return ("success", value)
