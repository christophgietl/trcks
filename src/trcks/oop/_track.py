from __future__ import annotations

import dataclasses
from typing import Generic

from trcks._typing_extensions import TypeVar

_Core_co = TypeVar("_Core_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class Track(Generic[_Core_co]):
    core: _Core_co


__all__ = ["Track"]
