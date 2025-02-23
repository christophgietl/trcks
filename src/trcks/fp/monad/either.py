from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Literal, TypeVar, Union

if TYPE_CHECKING:
    from collections.abc import Callable

if sys.version_info >= (3, 11):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_L = TypeVar("_L")
_L1 = TypeVar("_L1")
_L2 = TypeVar("_L2")
_R = TypeVar("_R")
_R1 = TypeVar("_R1")
_R2 = TypeVar("_R2")

_L_co = TypeVar("_L_co", covariant=True)
_R_co = TypeVar("_R_co", covariant=True)


Left: TypeAlias = tuple[Literal["left"], _L_co]
Right: TypeAlias = tuple[Literal["right"], _R_co]
Either: TypeAlias = Union[Left[_L_co], Right[_R_co]]


def flat_map_left(
    f: Callable[[_L1], Either[_L2, _R2]],
) -> Callable[[Either[_L1, _R1]], Either[_L2, _R1 | _R2]]:
    def mapped_f(ethr: Either[_L1, _R1]) -> Either[_L2, _R1 | _R2]:
        return f(ethr[1]) if ethr[0] == "left" else ethr

    return mapped_f


def flat_map_right(
    f: Callable[[_R1], Either[_L2, _R2]],
) -> Callable[[Either[_L1, _R1]], Either[_L1 | _L2, _R2]]:
    def mapped_f(ethr: Either[_L1, _R1]) -> Either[_L1 | _L2, _R2]:
        return f(ethr[1]) if ethr[0] == "right" else ethr

    return mapped_f


def map_left(
    f: Callable[[_L1], _L2],
) -> Callable[[Either[_L1, _R1]], Either[_L2, _R1]]:
    def mapped_f(ethr: Either[_L1, _R1]) -> Either[_L2, _R1]:
        return of_left(f(ethr[1])) if ethr[0] == "left" else ethr

    return mapped_f


def map_right(
    f: Callable[[_R1], _R2],
) -> Callable[[Either[_L1, _R1]], Either[_L1, _R2]]:
    def mapped_f(ethr: Either[_L1, _R1]) -> Either[_L1, _R2]:
        return of_right(f(ethr[1])) if ethr[0] == "right" else ethr

    return mapped_f


def of_left(value: _L) -> Left[_L]:
    return ("left", value)


def of_right(value: _R) -> Right[_R]:
    return ("right", value)
