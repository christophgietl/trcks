from __future__ import annotations

import dataclasses
from collections.abc import Awaitable
from typing import TYPE_CHECKING, TypeVar

from trcks.fp.monad import awaitable
from trcks.oop import _track

if TYPE_CHECKING:
    from collections.abc import Callable

_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AsyncSingleTrack(_track.Track[Awaitable[_T_co]]):
    def map(self, f: Callable[[_T_co], _T]) -> AsyncSingleTrack[_T]:
        f_mapped = awaitable.map_(f)
        return AsyncSingleTrack(f_mapped(self.core))
