import asyncio
import math
from collections.abc import Coroutine
from typing import Final, Literal

import pytest

from trcks import Result
from trcks.oop import AwaitableRailway, AwaitableResultRailway, Railway, ResultRailway

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


class TestAwaitableRailway:
    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_awaitable_railway_wraps_awaitable(self, value: object) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        assert AwaitableRailway(awaitable).core is awaitable

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_wraps_value(self, value: object) -> None:
        assert await AwaitableRailway.construct(value).core == value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_from_awaitable_wraps_awaitable(
        self, value: object
    ) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        assert AwaitableRailway.construct_from_awaitable(awaitable).core is awaitable

    async def test_core_as_coroutine_is_coroutine(self) -> None:
        core_as_coroutine = AwaitableRailway.construct(1).core_as_coroutine
        assert isinstance(core_as_coroutine, Coroutine)
        assert await core_as_coroutine == 1

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_maps_value(self, value: float) -> None:
        assert await AwaitableRailway.construct(value).map(_double).core == _double(
            value
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_maps_value(self, value: float) -> None:
        assert await AwaitableRailway.construct(value).map_to_awaitable(
            _double_slowly
        ).core == await _double_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_maps_value(self, value: float) -> None:
        assert await AwaitableRailway.construct(value).map_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_result_maps_maps_value(self, value: float) -> None:
        assert await AwaitableRailway.construct(value).map_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)


class TestAwaitableResultRailway:
    @pytest.mark.parametrize("result", _RESULTS)
    async def test_awaitable_result_railway_wraps_awaitable_result(
        self, result: Result[object, object]
    ) -> None:
        awaitable_result = asyncio.create_task(asyncio.sleep(0.001, result=result))
        assert AwaitableResultRailway(awaitable_result).core is awaitable_result

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_failure_wraps_value(self, value: object) -> None:
        awaited_core = await AwaitableResultRailway.construct_failure(value).core
        assert awaited_core[0] == "failure"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_failure_from_awaitable_wraps_value(
        self, value: object
    ) -> None:
        awaited_core = await AwaitableResultRailway.construct_failure_from_awaitable(
            asyncio.create_task(asyncio.sleep(0.001, result=value))
        ).core
        assert awaited_core[0] == "failure"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_construct_from_awaitable_result_wraps_awaitable_result(
        self, result: Result[object, object]
    ) -> None:
        awaitable_result = asyncio.create_task(asyncio.sleep(0.001, result=result))
        assert (
            AwaitableResultRailway.construct_from_awaitable_result(
                awaitable_result
            ).core
            is awaitable_result
        )

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_construct_from_result_wraps_result(
        self, result: Result[object, object]
    ) -> None:
        assert await AwaitableResultRailway.construct_from_result(result).core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_success_wraps_value(self, value: object) -> None:
        awaited_core = await AwaitableResultRailway.construct_success(value).core
        assert awaited_core[0] == "success"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_success_from_awaitable_wraps_value(
        self, value: object
    ) -> None:
        awaited_core = await AwaitableResultRailway.construct_success_from_awaitable(
            asyncio.create_task(asyncio.sleep(0.001, result=value))
        ).core
        assert awaited_core[0] == "success"
        assert awaited_core[1] is value

    async def test_core_as_coroutine_is_coroutine(self) -> None:
        core_as_coroutine = AwaitableResultRailway.construct_success(
            1
        ).core_as_coroutine
        assert isinstance(core_as_coroutine, Coroutine)
        assert await core_as_coroutine == ("success", 1)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_does_not_change_success(self, value: object) -> None:
        success: Final = ("success", value)
        assert (
            await AwaitableResultRailway.construct_from_result(success)
            .map_failure(_double)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_maps_failure_value(self, value: float) -> None:
        assert await AwaitableResultRailway.construct_failure(value).map_failure(
            _double
        ).core == ("failure", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_to_awaitable_does_not_change_success(
        self, value: object
    ) -> None:
        success: Final = ("success", value)
        assert (
            await AwaitableResultRailway.construct_from_result(success)
            .map_failure_to_awaitable(_double_slowly)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_maps_failure_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultRailway.construct_failure(
            value
        ).map_failure_to_awaitable(_double_slowly).core == (
            "failure",
            await _double_slowly(value),
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_does_not_change_success(
        self, value: float
    ) -> None:
        success: Final = ("success", value)
        assert (
            await AwaitableResultRailway.construct_from_result(success)
            .map_failure_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_maps_failure_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultRailway.construct_failure(
            value
        ).map_failure_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_result_does_not_change_success(
        self, value: float
    ) -> None:
        success: Final = ("success", value)
        assert (
            await AwaitableResultRailway.construct_from_result(success)
            .map_failure_to_result(_get_square_root_safely)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_result_maps_failure_value(self, value: float) -> None:
        assert await AwaitableResultRailway.construct_failure(
            value
        ).map_failure_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_does_not_change_failure(self, value: object) -> None:
        failure: Final = ("failure", value)
        assert (
            await AwaitableResultRailway.construct_from_result(failure)
            .map_success(_double)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_maps_success_value(self, value: float) -> None:
        assert await AwaitableResultRailway.construct_success(value).map_success(
            _double
        ).core == ("success", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_to_awaitable_does_not_change_failure(
        self, value: object
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await AwaitableResultRailway.construct_from_result(failure)
            .map_success_to_awaitable(_double_slowly)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_maps_success_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultRailway.construct_success(
            value
        ).map_success_to_awaitable(_double_slowly).core == (
            "success",
            await _double_slowly(value),
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_does_not_change_failure(
        self, value: float
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await AwaitableResultRailway.construct_from_result(failure)
            .map_success_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_maps_success_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultRailway.construct_success(
            value
        ).map_success_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_result_does_not_change_failure(
        self, value: float
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await AwaitableResultRailway.construct_from_result(failure)
            .map_success_to_result(_get_square_root_safely)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_result_maps_success_value(self, value: float) -> None:
        assert await AwaitableResultRailway.construct_success(
            value
        ).map_success_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_track_equals_first_element_of_result(
        self, result: Result[object, object]
    ) -> None:
        assert (
            await AwaitableResultRailway.construct_from_result(result).track
            == result[0]
        )

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_value_equals_second_element_of_result(
        self, result: Result[object, object]
    ) -> None:
        assert (
            await AwaitableResultRailway.construct_from_result(result).value
            == result[1]
        )


class TestRailway:
    @pytest.mark.parametrize("value", _OBJECTS)
    def test_railway_wraps_value(self, value: object) -> None:
        assert Railway(value).core is value

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_wraps_value(self, value: object) -> None:
        assert Railway.construct(value).core is value

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_maps_value(self, value: float) -> None:
        assert Railway(value).map(_double).core == _double(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_to_awaitable_maps_value(self, value: object) -> None:
        assert await Railway(value).map_to_awaitable(
            _stringify_slowly
        ).core == await _stringify_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_to_result_maps_value(self, value: float) -> None:
        assert Railway(value).map_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_maps_value(self, value: float) -> None:
        assert await Railway(value).map_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)


class TestResultRailway:
    @pytest.mark.parametrize("result", _RESULTS)
    def test_result_railway_wraps_result(self, result: Result[object, object]) -> None:
        assert ResultRailway(result).core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_failure_wraps_value(self, value: object) -> None:
        result_railway = ResultRailway.construct_failure(value)
        assert result_railway.core[0] == "failure"
        assert result_railway.core[1] is value

    @pytest.mark.parametrize("result", _RESULTS)
    def test_construct_from_result_wraps_result(
        self, result: Result[object, object]
    ) -> None:
        assert ResultRailway.construct_from_result(result).core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_success_wraps_value(self, value: object) -> None:
        result_railway = ResultRailway.construct_success(value)
        assert result_railway.core[0] == "success"
        assert result_railway.core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_map_failure_does_not_change_success(self, value: object) -> None:
        success: Final = ("success", value)
        assert ResultRailway(success).map_failure(_double).core is success

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_maps_failure_value(self, value: float) -> None:
        assert ResultRailway.construct_failure(value).map_failure(_double).core == (
            "failure",
            _double(value),
        )

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_to_awaitable_does_not_change_success(
        self, value: object
    ) -> None:
        success: Final = ("success", value)
        assert (
            await ResultRailway(success).map_failure_to_awaitable(_double_slowly).core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_maps_failure_value(
        self, value: float
    ) -> None:
        assert await ResultRailway.construct_failure(value).map_failure_to_awaitable(
            _double_slowly
        ).core == (
            "failure",
            await _double_slowly(value),
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_does_not_change_success(
        self, value: float
    ) -> None:
        success: Final = ("success", value)
        assert (
            await ResultRailway(success)
            .map_failure_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_maps_failure_value(
        self, value: float
    ) -> None:
        assert await ResultRailway.construct_failure(
            value
        ).map_failure_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_to_result_does_not_change_success(self, value: float) -> None:
        success: Final = ("success", value)
        assert (
            ResultRailway(success).map_failure_to_result(_get_square_root_safely).core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_to_result_maps_failure_value(self, value: float) -> None:
        assert ResultRailway.construct_failure(value).map_failure_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_map_success_does_not_change_failure(self, value: object) -> None:
        failure: Final = ("failure", value)
        assert ResultRailway(failure).map_success(_double).core is failure

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_maps_success_value(self, value: float) -> None:
        assert ResultRailway.construct_success(value).map_success(_double).core == (
            "success",
            _double(value),
        )

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_to_awaitable_does_not_change_failure(
        self, value: object
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await ResultRailway(failure).map_success_to_awaitable(_double_slowly).core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_maps_success_value(
        self, value: float
    ) -> None:
        assert await ResultRailway.construct_success(value).map_success_to_awaitable(
            _double_slowly
        ).core == (
            "success",
            await _double_slowly(value),
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_does_not_change_failure(
        self, value: float
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await ResultRailway(failure)
            .map_success_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_maps_success_value(
        self, value: float
    ) -> None:
        assert await ResultRailway.construct_success(
            value
        ).map_success_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_to_result_does_not_change_failure(self, value: float) -> None:
        failure: Final = ("failure", value)
        assert (
            ResultRailway(failure).map_success_to_result(_get_square_root_safely).core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_to_result_maps_success_value(self, value: float) -> None:
        assert ResultRailway.construct_success(value).map_success_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("result", _RESULTS)
    def test_track_equals_first_element_of_result(
        self, result: Result[object, object]
    ) -> None:
        assert ResultRailway.construct_from_result(result).track == result[0]

    @pytest.mark.parametrize("result", _RESULTS)
    def test_value_equals_second_element_of_result(
        self, result: Result[object, object]
    ) -> None:
        assert ResultRailway(result).value == result[1]
