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


LeftTrack: TypeAlias = tuple[Literal["left"], _L_co]
RightTrack: TypeAlias = tuple[Literal["right"], _R_co]
DualTrack: TypeAlias = Union[LeftTrack[_L_co], RightTrack[_R_co]]


def flat_map_left(
    f: Callable[[_L1], DualTrack[_L2, _R2]],
) -> Callable[[DualTrack[_L1, _R1]], DualTrack[_L2, _R1 | _R2]]:
    def mapped_f(dt: DualTrack[_L1, _R1]) -> DualTrack[_L2, _R1 | _R2]:
        return f(dt[1]) if dt[0] == "left" else dt

    return mapped_f


def flat_map_right(
    f: Callable[[_R1], DualTrack[_L2, _R2]],
) -> Callable[[DualTrack[_L1, _R1]], DualTrack[_L1 | _L2, _R2]]:
    def mapped_f(dt: DualTrack[_L1, _R1]) -> DualTrack[_L1 | _L2, _R2]:
        return f(dt[1]) if dt[0] == "right" else dt

    return mapped_f


def map_left(
    f: Callable[[_L1], _L2],
) -> Callable[[DualTrack[_L1, _R1]], DualTrack[_L2, _R1]]:
    def mapped_f(dt: DualTrack[_L1, _R1]) -> DualTrack[_L2, _R1]:
        return of_left(f(dt[1])) if dt[0] == "left" else dt

    return mapped_f


def map_right(
    f: Callable[[_R1], _R2],
) -> Callable[[DualTrack[_L1, _R1]], DualTrack[_L1, _R2]]:
    def mapped_f(dt: DualTrack[_L1, _R1]) -> DualTrack[_L1, _R2]:
        return of_right(f(dt[1])) if dt[0] == "right" else dt

    return mapped_f


def of_left(value: _L) -> LeftTrack[_L]:
    return ("left", value)


def of_right(value: _R) -> RightTrack[_R]:
    return ("right", value)
