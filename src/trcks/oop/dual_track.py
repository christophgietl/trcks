from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import result
from trcks.oop import _track

if TYPE_CHECKING:
    from collections.abc import Callable

if sys.version_info >= (3, 11):
    from typing import Never, TypeAlias
else:
    from typing_extensions import Never, TypeAlias

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)

Result: TypeAlias = result.Result[_F_co, _S_co]


@dataclasses.dataclass(frozen=True)
class DualTrack(_track.Track[Result[_F_co, _S_co]]):
    @staticmethod
    def failure(value: _F) -> DualTrack[_F, Never]:
        return DualTrack(result.of_failure(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> DualTrack[_F, _S_co]:
        f_mapped = result.map_failure(f)
        return DualTrack(f_mapped(self.core))

    def map_success(self, f: Callable[[_S_co], _S]) -> DualTrack[_F_co, _S]:
        f_mapped = result.map_success(f)
        return DualTrack(f_mapped(self.core))

    @staticmethod
    def success(value: _S) -> DualTrack[Never, _S]:
        return DualTrack(result.of_success(value))

    @property
    def track(self) -> Literal["failure", "success"]:
        return self.core[0]

    @property
    def value(self) -> _F_co | _S_co:
        return self.core[1]
