from __future__ import annotations

import asyncio
import inspect
import math
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Final, Literal, TypeAlias

import pytest

from trcks.oop import (
    AwaitableResultTupleWrapper,
    AwaitableResultWrapper,
    AwaitableTupleWrapper,
    AwaitableWrapper,
    ResultTupleWrapper,
    ResultWrapper,
    TupleWrapper,
    Wrapper,
)

if TYPE_CHECKING:
    import sys
    from collections.abc import Mapping
    from types import FunctionType

    from trcks import Result, ResultTuple

    if sys.version_info >= (3, 11):
        from typing import Never
    else:
        from typing_extensions import Never

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]

_TO_PAIR: Final[Callable[[int], tuple[int, int]]] = lambda n: (n, n)  # noqa: E731

_FLOATS: Final[tuple[float, ...]] = (0.0, 1.5, -2.3, 100.75, math.pi, -math.e)
_OBJECTS: Final[tuple[object, ...]] = (
    21,
    _TO_PAIR,
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

_MAP_AND_TAP_METHODS: Final[Mapping[str, FunctionType]] = {
    f"{cls.__qualname__}.{name}": method
    for cls in (
        Wrapper,
        AwaitableWrapper,
        ResultWrapper,
        TupleWrapper,
        AwaitableTupleWrapper,
        AwaitableResultWrapper,
        ResultTupleWrapper,
        AwaitableResultTupleWrapper,
    )
    for name, method in inspect.getmembers(cls, inspect.isfunction)
    if name.startswith(("map", "tap"))
}


def _double(x: float) -> float:
    return x * 2.0


async def _double_slowly(x: float) -> float:
    await asyncio.sleep(0.001)
    return _double(x)


def _get_square_root_safely(x: float) -> Result[Literal["negative"], float]:
    if x < 0:
        return "failure", "negative"
    return "success", math.sqrt(x)


async def _get_square_root_safely_and_slowly(
    x: float,
) -> Result[Literal["negative"], float]:
    if x < 0:
        return "failure", "negative"
    await asyncio.sleep(0.001)
    return "success", math.sqrt(x)


async def _stringify_slowly(o: object) -> str:
    await asyncio.sleep(0.001)
    return str(o)


@pytest.mark.parametrize(
    ("name", "method"),
    [
        pytest.param(name, method, id=name)
        for name, method in _MAP_AND_TAP_METHODS.items()
    ],
)
def test_method_accepts_args_and_kwargs(name: str, method: FunctionType) -> None:
    kinds = {
        parameter.kind for parameter in inspect.signature(method).parameters.values()
    }
    assert inspect.Parameter.VAR_POSITIONAL in kinds, f"{name} does not accept *args"
    assert inspect.Parameter.VAR_KEYWORD in kinds, f"{name} does not accept **kwargs"


def test_more_than_fifty_methods_were_collected() -> None:
    assert len(_MAP_AND_TAP_METHODS) > 50  # noqa: PLR2004


class TestAwaitableResultTupleWrapper:
    async def test_map_successes_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: ResultTuple[Never, None] = await (
            AwaitableResultTupleWrapper.construct_successes("input")
            .map_successes(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", (None,))
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    async def test_tap_successes_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: ResultTuple[Never, str] = await (
            AwaitableResultTupleWrapper.construct_successes("input")
            .tap_successes(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", ("input",))
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestAwaitableResultWrapper:
    @pytest.mark.parametrize("result", _RESULTS)
    async def test_awaitable_result_wrapper_wraps_awaitable_result(
        self, result: Result[object, object]
    ) -> None:
        awaitable_result = asyncio.create_task(asyncio.sleep(0.001, result=result))
        assert AwaitableResultWrapper(awaitable_result).core is awaitable_result

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_failure_from_awaitable_wraps_value(
        self, value: object
    ) -> None:
        awaited_core = await AwaitableResultWrapper.construct_failure_from_awaitable(
            asyncio.create_task(asyncio.sleep(0.001, result=value))
        ).core
        assert awaited_core[0] == "failure"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_failure_wraps_value(self, value: object) -> None:
        awaited_core = await AwaitableResultWrapper.construct_failure(value).core
        assert awaited_core[0] == "failure"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_construct_from_awaitable_result_wraps_awaitable_result(
        self, result: Result[object, object]
    ) -> None:
        awaitable_result = asyncio.create_task(asyncio.sleep(0.001, result=result))
        assert (
            AwaitableResultWrapper.construct_from_awaitable_result(
                awaitable_result
            ).core
            is awaitable_result
        )

    @pytest.mark.parametrize("result", _RESULTS)
    async def test_construct_from_result_wraps_result(
        self, result: Result[object, object]
    ) -> None:
        assert await AwaitableResultWrapper.construct_from_result(result).core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_success_from_awaitable_wraps_value(
        self, value: object
    ) -> None:
        awaited_core = await AwaitableResultWrapper.construct_success_from_awaitable(
            asyncio.create_task(asyncio.sleep(0.001, result=value))
        ).core
        assert awaited_core[0] == "success"
        assert awaited_core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_success_wraps_value(self, value: object) -> None:
        awaited_core = await AwaitableResultWrapper.construct_success(value).core
        assert awaited_core[0] == "success"
        assert awaited_core[1] is value

    async def test_core_as_coroutine_is_coroutine(self) -> None:
        core_as_coroutine = AwaitableResultWrapper.construct_success(
            1
        ).core_as_coroutine
        assert isinstance(core_as_coroutine, Coroutine)
        assert await core_as_coroutine == ("success", 1)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_does_not_change_success(self, value: object) -> None:
        success: Final = ("success", value)
        assert (
            await AwaitableResultWrapper.construct_from_result(success)
            .map_failure(_double)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_maps_failure_value(self, value: float) -> None:
        assert await AwaitableResultWrapper.construct_failure(value).map_failure(
            _double
        ).core == ("failure", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_to_awaitable_does_not_change_success(
        self, value: object
    ) -> None:
        success: Final = ("success", value)
        assert (
            await AwaitableResultWrapper.construct_from_result(success)
            .map_failure_to_awaitable(_double_slowly)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_maps_failure_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultWrapper.construct_failure(
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
            await AwaitableResultWrapper.construct_from_result(success)
            .map_failure_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_maps_failure_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultWrapper.construct_failure(
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
            await AwaitableResultWrapper.construct_from_result(success)
            .map_failure_to_result(_get_square_root_safely)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_result_maps_failure_value(self, value: float) -> None:
        assert await AwaitableResultWrapper.construct_failure(
            value
        ).map_failure_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_does_not_change_failure(self, value: object) -> None:
        failure: Final = ("failure", value)
        assert (
            await AwaitableResultWrapper.construct_from_result(failure)
            .map_success(_double)
            .core
            is failure
        )

    async def test_map_success_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: Result[Never, None] = await (
            AwaitableResultWrapper.construct_success("input")
            .map_success(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", None)
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_maps_success_value(self, value: float) -> None:
        assert await AwaitableResultWrapper.construct_success(value).map_success(
            _double
        ).core == ("success", _double(value))

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_to_awaitable_does_not_change_failure(
        self, value: object
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await AwaitableResultWrapper.construct_from_result(failure)
            .map_success_to_awaitable(_double_slowly)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_maps_success_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultWrapper.construct_success(
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
            await AwaitableResultWrapper.construct_from_result(failure)
            .map_success_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_maps_success_value(
        self, value: float
    ) -> None:
        assert await AwaitableResultWrapper.construct_success(
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
            await AwaitableResultWrapper.construct_from_result(failure)
            .map_success_to_result(_get_square_root_safely)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_result_maps_success_value(self, value: float) -> None:
        assert await AwaitableResultWrapper.construct_success(
            value
        ).map_success_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    async def test_tap_success_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: Result[Never, str] = await (
            AwaitableResultWrapper.construct_success("input")
            .tap_success(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", "input")
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestAwaitableTupleWrapper:
    async def test_map_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: tuple[None, ...] = await (
            AwaitableTupleWrapper.construct("input")
            .map(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == (None,)
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    async def test_tap_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: tuple[str, ...] = await (
            AwaitableTupleWrapper.construct("input")
            .tap(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("input",)
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestAwaitableWrapper:
    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_awaitable_wrapper_wraps_awaitable(self, value: object) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        assert AwaitableWrapper(awaitable).core is awaitable

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_from_awaitable_wraps_awaitable(
        self, value: object
    ) -> None:
        awaitable = asyncio.create_task(asyncio.sleep(0.001, result=value))
        assert AwaitableWrapper.construct_from_awaitable(awaitable).core is awaitable

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_construct_wraps_value(self, value: object) -> None:
        assert await AwaitableWrapper.construct(value).core == value

    async def test_core_as_coroutine_is_coroutine(self) -> None:
        core_as_coroutine = AwaitableWrapper.construct(1).core_as_coroutine
        assert isinstance(core_as_coroutine, Coroutine)
        assert await core_as_coroutine == 1

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_maps_value(self, value: float) -> None:
        assert await AwaitableWrapper.construct(value).map(_double).core == _double(
            value
        )

    async def test_map_to_awaitable_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        async def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: None = await (  # type: ignore[func-returns-value]
            AwaitableWrapper.construct("input")
            .map_to_awaitable(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output is None
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_maps_value(self, value: float) -> None:
        assert await AwaitableWrapper.construct(value).map_to_awaitable(
            _double_slowly
        ).core == await _double_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_maps_value(self, value: float) -> None:
        assert await AwaitableWrapper.construct(value).map_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_result_maps_maps_value(self, value: float) -> None:
        assert await AwaitableWrapper.construct(value).map_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    async def test_tap_to_awaitable_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        async def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: str = await (
            AwaitableWrapper.construct("input")
            .tap_to_awaitable(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == "input"
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestResultTupleWrapper:
    def test_map_successes_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: ResultTuple[Never, None] = (
            ResultTupleWrapper.construct_successes("input")
            .map_successes(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", (None,))
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    def test_tap_successes_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: ResultTuple[Never, str] = (
            ResultTupleWrapper.construct_successes("input")
            .tap_successes(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", ("input",))
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestResultWrapper:
    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_failure_wraps_value(self, value: object) -> None:
        result_wrapper = ResultWrapper.construct_failure(value)
        assert result_wrapper.core[0] == "failure"
        assert result_wrapper.core[1] is value

    @pytest.mark.parametrize("result", _RESULTS)
    def test_construct_from_result_wraps_result(
        self, result: Result[object, object]
    ) -> None:
        assert ResultWrapper.construct_from_result(result).core is result

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_success_wraps_value(self, value: object) -> None:
        result_wrapper = ResultWrapper.construct_success(value)
        assert result_wrapper.core[0] == "success"
        assert result_wrapper.core[1] is value

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_map_failure_does_not_change_success(self, value: object) -> None:
        success: Final = ("success", value)
        assert ResultWrapper(success).map_failure(_double).core is success

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_maps_failure_value(self, value: float) -> None:
        assert ResultWrapper.construct_failure(value).map_failure(_double).core == (
            "failure",
            _double(value),
        )

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_failure_to_awaitable_does_not_change_success(
        self, value: object
    ) -> None:
        success: Final = ("success", value)
        assert (
            await ResultWrapper(success).map_failure_to_awaitable(_double_slowly).core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_maps_failure_value(
        self, value: float
    ) -> None:
        assert await ResultWrapper.construct_failure(value).map_failure_to_awaitable(
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
            await ResultWrapper(success)
            .map_failure_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_failure_to_awaitable_result_maps_failure_value(
        self, value: float
    ) -> None:
        assert await ResultWrapper.construct_failure(
            value
        ).map_failure_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_to_result_does_not_change_success(self, value: float) -> None:
        success: Final = ("success", value)
        assert (
            ResultWrapper(success).map_failure_to_result(_get_square_root_safely).core
            is success
        )

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_failure_to_result_maps_failure_value(self, value: float) -> None:
        assert ResultWrapper.construct_failure(value).map_failure_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_map_success_does_not_change_failure(self, value: object) -> None:
        failure: Final = ("failure", value)
        assert ResultWrapper(failure).map_success(_double).core is failure

    def test_map_success_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: Result[Never, None] = (
            ResultWrapper.construct_success("input")
            .map_success(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", None)
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_maps_success_value(self, value: float) -> None:
        assert ResultWrapper.construct_success(value).map_success(_double).core == (
            "success",
            _double(value),
        )

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_success_to_awaitable_does_not_change_failure(
        self, value: object
    ) -> None:
        failure: Final = ("failure", value)
        assert (
            await ResultWrapper(failure).map_success_to_awaitable(_double_slowly).core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_maps_success_value(
        self, value: float
    ) -> None:
        assert await ResultWrapper.construct_success(value).map_success_to_awaitable(
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
            await ResultWrapper(failure)
            .map_success_to_awaitable_result(_get_square_root_safely_and_slowly)
            .core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_success_to_awaitable_result_maps_success_value(
        self, value: float
    ) -> None:
        assert await ResultWrapper.construct_success(
            value
        ).map_success_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_to_result_does_not_change_failure(self, value: float) -> None:
        failure: Final = ("failure", value)
        assert (
            ResultWrapper(failure).map_success_to_result(_get_square_root_safely).core
            is failure
        )

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_success_to_result_maps_success_value(self, value: float) -> None:
        assert ResultWrapper.construct_success(value).map_success_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    @pytest.mark.parametrize("result", _RESULTS)
    def test_result_wrapper_wraps_result(self, result: Result[object, object]) -> None:
        assert ResultWrapper(result).core is result

    def test_tap_success_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: Result[Never, str] = (
            ResultWrapper.construct_success("input")
            .tap_success(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("success", "input")
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestTupleWrapper:
    def test_map_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: tuple[None, ...] = (
            TupleWrapper.construct("input")
            .map(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == (None,)
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    def test_tap_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: tuple[str, ...] = (
            TupleWrapper.construct("input")
            .tap(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == ("input",)
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


class TestWrapper:
    @pytest.mark.parametrize("value", _OBJECTS)
    def test_construct_wraps_value(self, value: object) -> None:
        assert Wrapper.construct(value).core is value

    def test_map_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: None = (
            Wrapper.construct("input")
            .map(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output is None
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_maps_value(self, value: float) -> None:
        assert Wrapper(value).map(_double).core == _double(value)

    @pytest.mark.parametrize("value", _OBJECTS)
    async def test_map_to_awaitable_maps_value(self, value: object) -> None:
        assert await Wrapper(value).map_to_awaitable(
            _stringify_slowly
        ).core == await _stringify_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    async def test_map_to_awaitable_result_maps_value(self, value: float) -> None:
        assert await Wrapper(value).map_to_awaitable_result(
            _get_square_root_safely_and_slowly
        ).core == await _get_square_root_safely_and_slowly(value)

    @pytest.mark.parametrize("value", _FLOATS)
    def test_map_to_result_maps_value(self, value: float) -> None:
        assert Wrapper(value).map_to_result(
            _get_square_root_safely
        ).core == _get_square_root_safely(value)

    def test_tap_forwards_args_and_kwargs(self) -> None:
        recorded_calls: _RecordedCalls = []

        def record_call(*args: object, **kwargs: object) -> None:
            recorded_calls.append((args, kwargs))

        output: str = (
            Wrapper.construct("input")
            .tap(
                record_call,
                "extra",  # pyrefly: ignore [bad-argument-count]
                extra_kw="kw",
            )
            .core
        )

        assert output == "input"
        assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]

    @pytest.mark.parametrize("value", _OBJECTS)
    def test_wrapper_wraps_value(self, value: object) -> None:
        assert Wrapper(value).core is value
