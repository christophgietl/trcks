import asyncio
import math
from typing import Final, Literal

import pytest

from trcks.oop import DualTrack, Result, SingleTrack

_FLOATS: Final[tuple[float, ...]] = (0.0, 1.5, -2.3, 100.75, math.pi, -math.e)
_OBJECTS: Final[tuple[object, ...]] = (
    21,
    lambda n: (n, n),
    "test",
    [1, 2, 3],
    {"a": 1},
)
_RESULTS: Final[tuple[Result[str, float], ...]] = (
    ("success", 21),
    ("failure", "negative"),
    ("success", math.sqrt(100.75)),
    ("success", math.sqrt(math.pi)),
    ("success", math.sqrt(math.e)),
)


def _double(x: float) -> float:
    return x * 2.0


async def _double_slowly(x: float) -> float:
    await asyncio.sleep(0.001)
    return _double(x)


def _get_square_root_safely(x: float) -> Result[Literal["negative"], float]:
    if x < 0:
        return ("failure", "negative")
    return ("success", math.sqrt(x))


async def _get_square_root_safely_and_slowly(
    x: float,
) -> Result[Literal["negative"], float]:
    if x < 0:
        return ("failure", "negative")
    await asyncio.sleep(0.001)
    return ("success", math.sqrt(x))


async def _stringify_slowly(o: object) -> str:
    await asyncio.sleep(0.001)
    return str(o)


class TestDualTrack:
    @pytest.mark.parametrize("result", _RESULTS)
    def test_dual_track_wraps_result(self, result: Result[object, object]) -> None:
        dual_track = DualTrack(result)
        assert dual_track.core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_failure_wraps_object(self, value: object) -> None:
        dual_track = DualTrack.construct_failure(value)
        assert dual_track.core[0] == "failure"
        assert dual_track.core[1] is value

    @pytest.mark.parametrize("result", _RESULTS)
    def test_construct_from_result_wraps_result(
        self, result: Result[object, object]
    ) -> None:
        dual_track = DualTrack.construct_from_result(result)
        assert dual_track.core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_success_wraps_object(self, value: object) -> None:
        dual_track = DualTrack.construct_success(value)
        assert dual_track.core[0] == "success"
        assert dual_track.core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_map_failure_does_not_change_success_core(self, value: object) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_failure(_double)
        assert dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_maps_failure_core(self, value: float) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_failure(_double)
        assert dual_track.core == ("failure", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_to_awaitable_does_not_change_success_core(
        self, value: object
    ) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_failure_to_awaitable(_double_slowly)
        assert await dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_maps_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_failure_to_awaitable(_double_slowly)
        assert await dual_track.core == ("failure", await _double_slowly(value))

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_does_not_change_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_failure_to_awaitable_result(
            _get_square_root_safely_and_slowly
        )
        assert await dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_maps_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_failure_to_awaitable_result(
            _get_square_root_safely_and_slowly
        )
        assert await dual_track.core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_to_result_does_not_change_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_failure_to_result(_get_square_root_safely)
        assert dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_to_result_maps_failure_core(self, value: float) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_failure_to_result(_get_square_root_safely)
        assert dual_track.core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_map_success_does_not_change_failure_core(self, value: object) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_success(_double)
        assert dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_maps_success_core(self, value: float) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_success(_double)
        assert dual_track.core == ("success", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_to_awaitable_does_not_change_failure_core(
        self, value: object
    ) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_success_to_awaitable(_double_slowly)
        assert await dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_maps_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_success_to_awaitable(_double_slowly)
        assert await dual_track.core == ("success", await _double_slowly(value))

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_does_not_change_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_success_to_awaitable_result(
            _get_square_root_safely_and_slowly
        )
        assert await dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_maps_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_success_to_awaitable_result(
            _get_square_root_safely_and_slowly
        )
        assert await dual_track.core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_to_result_does_not_change_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        dual_track = DualTrack(core).map_success_to_result(_get_square_root_safely)
        assert dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_to_result_maps_success_core(self, value: float) -> None:
        core: Final = ("success", value)
        dual_track = DualTrack(core).map_success_to_result(_get_square_root_safely)
        assert dual_track.core == _get_square_root_safely(value)

    def test_track_equals_failure_for_failure_core(self) -> None:
        assert DualTrack(("failure", 123)).track == "failure"

    def test_track_equals_success_for_success_core(self) -> None:
        assert DualTrack(("success", 123)).track == "success"

    @pytest.mark.parametrize("result", _RESULTS)
    def test_value_equals_result_value(self, result: Result[object, object]) -> None:
        assert DualTrack(result).value == result[1]


class TestSingleTrack:
    @pytest.mark.parametrize("core", _OBJECTS)
    def test_single_track_wraps_object(self, core: object) -> None:
        single_track = SingleTrack(core)
        assert single_track.core is core

    @pytest.mark.parametrize("core", _OBJECTS)
    def test_construct_wraps_object(self, core: object) -> None:
        single_track = SingleTrack.construct(core)
        assert single_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_applies_function_to_core(self, value: float) -> None:
        assert SingleTrack(value).map(_double).core == _double(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_to_awaitable_applies_function_to_core(
        self, value: object
    ) -> None:
        assert await SingleTrack(value).map_to_awaitable(
            _stringify_slowly
        ).core == await _stringify_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_to_result_applies_function_to_core(self, value: float) -> None:
        assert SingleTrack(value).map_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_applies_function_to_core(
        self, value: float
    ) -> None:
        assert await SingleTrack(value).map_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)
