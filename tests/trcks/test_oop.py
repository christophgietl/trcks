import asyncio
import math
from typing import TYPE_CHECKING, Final, Literal

import pytest

from trcks.oop import AsyncDualTrack, AsyncSingleTrack, DualTrack, Result, SingleTrack

if TYPE_CHECKING:
    from trcks._typing_extensions import Never

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


class TestAsyncDualTrack:
    @pytest.mark.parametrize("result", _RESULTS)
    async def test_async_dual_track_wraps_awaitable_result(
        self, result: Result[object, object]
    ) -> None:
        awaitable_result = asyncio.create_task(asyncio.sleep(0.001, result=result))
        async_dual_track = AsyncDualTrack(awaitable_result)
        assert async_dual_track.core is awaitable_result

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_failure_wraps_object(self, value: object) -> None:
        async_dual_track = AsyncDualTrack.construct_failure(value)
        awaited_core = await async_dual_track.core
        assert awaited_core[0] == "failure"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_failure_from_awaitable_wraps_object(
        self, value: object
    ) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        async_dual_track = AsyncDualTrack.construct_failure_from_awaitable(awaitable)
        awaited_core = await async_dual_track.core
        assert awaited_core[0] == "failure"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_construct_from_awaitable_result_wraps_awaitable_result(
        self, result: Result[object, object]
    ) -> None:
        awaitable_result = asyncio.create_task(asyncio.sleep(0.001, result=result))
        async_dual_track = AsyncDualTrack.construct_from_awaitable_result(
            awaitable_result
        )
        assert async_dual_track.core is awaitable_result

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_construct_from_result_wraps_result(
        self, result: Result[object, object]
    ) -> None:
        async_dual_track = AsyncDualTrack.construct_from_result(result)
        assert await async_dual_track.core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_success_wraps_object(self, value: object) -> None:
        async_dual_track = AsyncDualTrack.construct_success(value)
        awaited_core = await async_dual_track.core
        assert awaited_core[0] == "success"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_success_from_awaitable_wraps_object(
        self, value: object
    ) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        async_dual_track = AsyncDualTrack.construct_success_from_awaitable(awaitable)
        awaited_core = await async_dual_track.core
        assert awaited_core[0] == "success"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_does_not_change_success_core(
        self, value: object
    ) -> None:
        core: Final = ("success", value)
        async_dual_track = AsyncDualTrack.construct_from_result(core).map_failure(
            _double
        )
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_maps_failure_core(self, value: float) -> None:
        core: Final = ("failure", value)
        async_dual_track: AsyncDualTrack[float, Never] = (
            AsyncDualTrack.construct_from_result(core).map_failure(_double)
        )
        assert await async_dual_track.core == ("failure", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_to_awaitable_does_not_change_success_core(
        self, value: object
    ) -> None:
        core: Final = ("success", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_failure_to_awaitable(_double_slowly)
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_maps_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        async_dual_track: AsyncDualTrack[float, Never] = (
            AsyncDualTrack.construct_from_result(core).map_failure_to_awaitable(
                _double_slowly
            )
        )
        assert await async_dual_track.core == ("failure", await _double_slowly(value))

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_does_not_change_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_failure_to_awaitable_result(_get_square_root_safely_and_slowly)
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_maps_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_failure_to_awaitable_result(_get_square_root_safely_and_slowly)
        assert await async_dual_track.core == await _get_square_root_safely_and_slowly(
            value
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_result_does_not_change_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_failure_to_result(_get_square_root_safely)
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_result_maps_failure_core(self, value: float) -> None:
        core: Final = ("failure", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_failure_to_result(_get_square_root_safely)
        assert await async_dual_track.core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_does_not_change_failure_core(
        self, value: object
    ) -> None:
        core: Final = ("failure", value)
        async_dual_track = AsyncDualTrack.construct_from_result(core).map_success(
            _double
        )
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_maps_success_core(self, value: float) -> None:
        core: Final = ("success", value)
        async_dual_track: AsyncDualTrack[Never, float] = (
            AsyncDualTrack.construct_from_result(core).map_success(_double)
        )
        assert await async_dual_track.core == ("success", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_to_awaitable_does_not_change_failure_core(
        self, value: object
    ) -> None:
        core: Final = ("failure", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_success_to_awaitable(_double_slowly)
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_maps_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        async_dual_track: AsyncDualTrack[Never, float] = (
            AsyncDualTrack.construct_from_result(core).map_success_to_awaitable(
                _double_slowly
            )
        )
        assert await async_dual_track.core == ("success", await _double_slowly(value))

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_does_not_change_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_success_to_awaitable_result(_get_square_root_safely_and_slowly)
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_maps_success_core(
        self, value: float
    ) -> None:
        core: Final = ("success", value)
        async_dual_track: AsyncDualTrack[Literal["negative"], float] = (
            AsyncDualTrack.construct_from_result(core).map_success_to_awaitable_result(
                _get_square_root_safely_and_slowly
            )
        )
        assert await async_dual_track.core == await _get_square_root_safely_and_slowly(
            value
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_result_does_not_change_failure_core(
        self, value: float
    ) -> None:
        core: Final = ("failure", value)
        async_dual_track = AsyncDualTrack.construct_from_result(
            core
        ).map_success_to_result(_get_square_root_safely)
        assert await async_dual_track.core is core

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_result_maps_success_core(self, value: float) -> None:
        core: Final = ("success", value)
        async_dual_track: AsyncDualTrack[Literal["negative"], float] = (
            AsyncDualTrack.construct_from_result(core).map_success_to_result(
                _get_square_root_safely
            )
        )
        assert await async_dual_track.core == _get_square_root_safely(value)

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_track_equals_result_track(
        self, result: Result[object, object]
    ) -> None:
        async_dual_track = AsyncDualTrack.construct_from_result(result)
        assert await async_dual_track.track == result[0]

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_value_equals_result_value(
        self, result: Result[object, object]
    ) -> None:
        async_dual_track = AsyncDualTrack.construct_from_result(result)
        assert await async_dual_track.value == result[1]


class TestAsyncSingleTrack:
    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_async_single_track_wraps_awaitable(self, value: object) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        async_single_track = AsyncSingleTrack(awaitable)
        assert async_single_track.core is awaitable

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_wraps_object(self, value: object) -> None:
        async_single_track = AsyncSingleTrack.construct(value)
        assert await async_single_track.core == value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_from_awaitable_wraps_awaitable(
        self, value: object
    ) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        async_single_track = AsyncSingleTrack.construct_from_awaitable(awaitable)
        assert async_single_track.core is awaitable

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_maps_applies_function_to_core(self, value: float) -> None:
        assert await AsyncSingleTrack.construct(value).map(_double).core == _double(
            value
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_applies_async_function_to_core(
        self, value: float
    ) -> None:
        assert await AsyncSingleTrack.construct(value).map_to_awaitable(
            _double_slowly
        ).core == await _double_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_applies_async_function_to_core(
        self, value: float
    ) -> None:
        assert await AsyncSingleTrack.construct(value).map_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_result_maps_applies_async_function_to_core(
        self, value: float
    ) -> None:
        assert await AsyncSingleTrack.construct(value).map_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)


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
