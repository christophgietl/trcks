from __future__ import annotations

import dataclasses
from typing import Generic

from trcks._typing import TypeVar

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class BaseRailway(Generic[_T_co]):
    freight: _T_co


__docformat__ = "google"
