from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, TypeVar

from trcks.oop import _track

if TYPE_CHECKING:
    from collections.abc import Callable

_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class SingleTrack(_track.Track[_T_co]):
    def map(self, f: Callable[[_T_co], _T]) -> SingleTrack[_T]:
        return SingleTrack(f(self.core))

    def map_to_single_track(
        self, f: Callable[[_T_co], SingleTrack[_T]]
    ) -> SingleTrack[_T]:
        return f(self.core)
