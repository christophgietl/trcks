from __future__ import annotations

import dataclasses
from collections.abc import Awaitable

from trcks._typing_extensions import TypeVar
from trcks.oop._track import Track

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AsyncTrack(Track[Awaitable[_T_co]]):
    @property
    async def core_as_coroutine(self) -> _T_co:
        return await self.core


__docformat__ = "google"
