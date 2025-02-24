from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import dual_track
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
class DualTrackHelper(_track.TrackHelper[dual_track.DualTrack[_L_co, _R_co]]):
    @staticmethod
    def left(value: _L) -> DualTrackHelper[_L, Never]:
        return DualTrackHelper(dual_track.of_left(value))

    def map_left(self, f: Callable[[_L_co], _L]) -> DualTrackHelper[_L, _R_co]:
        f_mapped = dual_track.map_left(f)
        return DualTrackHelper(f_mapped(self.core))

    def map_left_to_dual_track(
        self, f: Callable[[_L_co], DualTrackHelper[_L, _R]]
    ) -> DualTrackHelper[_L, _R_co | _R]:
        f_unwrapped = DualTrackHelper.unwrap_return_value(f)
        f_mapped = dual_track.flat_map_left(f_unwrapped)
        return DualTrackHelper(f_mapped(self.core))

    def map_right(self, f: Callable[[_R_co], _R]) -> DualTrackHelper[_L_co, _R]:
        f_mapped = dual_track.map_right(f)
        return DualTrackHelper(f_mapped(self.core))

    def map_right_to_dual_track(
        self, f: Callable[[_R_co], DualTrackHelper[_L, _R]]
    ) -> DualTrackHelper[_L_co | _L, _R]:
        f_unwrapped = DualTrackHelper.unwrap_return_value(f)
        f_mapped = dual_track.flat_map_right(f_unwrapped)
        return DualTrackHelper(f_mapped(self.core))

    @staticmethod
    def right(value: _R) -> DualTrackHelper[Never, _R]:
        return DualTrackHelper(dual_track.of_right(value))

    @property
    def track(self) -> Literal["left", "right"]:
        return self.core[0]

    @property
    def value(self) -> _L_co | _R_co:
        return self.core[1]
