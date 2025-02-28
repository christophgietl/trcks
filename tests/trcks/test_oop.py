import asyncio
import math
from typing import Literal

import pytest

from trcks.oop import Result, SingleTrack

_FLOATS = [0.0, 1.5, -2.3, 100.75, math.pi, -math.e]
_OBJECTS = [21, lambda n: (n, n), "test", [1, 2, 3], {"a": 1}]


class TestSingleTrack:
    @pytest.mark.parametrize("core", _OBJECTS)
    def test_single_track_wraps_object(self, core: object) -> None:
        track = SingleTrack(core)
        assert track.core is core

    @pytest.mark.parametrize("core", _OBJECTS)
    def test_construct_wraps_object(self, core: object) -> None:
        track = SingleTrack.construct(core)
        assert track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_applies_function_to_core(self, value: float) -> None:
        def double(x: float) -> float:
            return x * 2.0

        assert SingleTrack(value).map(double).core == double(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_to_awaitable_applies_function_to_core(
        self, value: object
    ) -> None:
        async def stringify_slowly(o: object) -> str:
            await asyncio.sleep(0.001)
            return str(o)

        assert await SingleTrack(value).map_to_awaitable(
            stringify_slowly
        ).core == await stringify_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_to_result_applies_function_to_core(self, value: float) -> None:
        def sqrt(n: float) -> Result[Literal["negative"], float]:
            if n < 0:
                return ("failure", "negative")
            return ("success", math.sqrt(value))

        assert SingleTrack(value).map_to_result(sqrt).core == sqrt(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_applies_function_to_core(
        self, value: float
    ) -> None:
        async def sqrt(n: float) -> Result[Literal["negative"], float]:
            if n < 0:
                return ("failure", "negative")
            await asyncio.sleep(0.001)
            return ("success", math.sqrt(value))

        assert await SingleTrack(value).map_to_awaitable_result(
            sqrt
        ).core == await sqrt(value)
