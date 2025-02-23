from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import either
from trcks.oop import _track

if TYPE_CHECKING:
    from collections.abc import Callable

if sys.version_info >= (3, 11):
    from typing import Never
else:
    from typing_extensions import Never

_L = TypeVar("_L")
_R = TypeVar("_R")

_L_co = TypeVar("_L_co", covariant=True)
_R_co = TypeVar("_R_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class DualTrack(_track.Track[either.Either[_L_co, _R_co]]):
    @staticmethod
    def left(value: _L) -> DualTrack[_L, Never]:
        return DualTrack(either.of_left(value))

    def map_left(self, f: Callable[[_L_co], _L]) -> DualTrack[_L, _R_co]:
        f_mapped = either.map_left(f)
        return DualTrack(f_mapped(self.core))

    def map_left_to_dual_track(
        self, f: Callable[[_L_co], DualTrack[_L, _R]]
    ) -> DualTrack[_L, _R_co | _R]:
        f_unwrapped = DualTrack.unwrap_return_value(f)
        f_mapped = either.flat_map_left(f_unwrapped)
        return DualTrack(f_mapped(self.core))

    def map_right(self, f: Callable[[_R_co], _R]) -> DualTrack[_L_co, _R]:
        f_mapped = either.map_right(f)
        return DualTrack(f_mapped(self.core))

    def map_right_to_dual_track(
        self, f: Callable[[_R_co], DualTrack[_L, _R]]
    ) -> DualTrack[_L_co | _L, _R]:
        f_unwrapped = DualTrack.unwrap_return_value(f)
        f_mapped = either.flat_map_right(f_unwrapped)
        return DualTrack(f_mapped(self.core))

    @staticmethod
    def right(value: _R) -> DualTrack[Never, _R]:
        return DualTrack(either.of_right(value))

    @property
    def track(self) -> Literal["left", "right"]:
        return self.core[0]

    @property
    def value(self) -> _L_co | _R_co:
        return self.core[1]
