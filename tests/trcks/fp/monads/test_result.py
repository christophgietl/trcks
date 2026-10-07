from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Final, TypeAlias

import pytest

from trcks.fp.monads import result as r

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from types import FunctionType
    from typing import Never

    from trcks import Result

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]

_MAP_AND_TAP_FUNCTIONS: Final[Mapping[str, FunctionType]] = {
    name: function
    for name, function in inspect.getmembers(r, inspect.isfunction)
    if name.startswith(("map", "tap"))
}


def test_collected_many_map_and_tap_functions() -> None:
    assert len(_MAP_AND_TAP_FUNCTIONS) > 35  # noqa: PLR2004


@pytest.mark.parametrize(
    ("name", "function"),
    [
        pytest.param(name, function, id=name)
        for name, function in _MAP_AND_TAP_FUNCTIONS.items()
    ],
)
def test_function_accepts_args_and_kwargs(
    name: str,
    function: FunctionType,
) -> None:
    kinds = {
        parameter.kind for parameter in inspect.signature(function).parameters.values()
    }
    assert inspect.Parameter.VAR_POSITIONAL in kinds, f"{name} does not accept *args"
    assert inspect.Parameter.VAR_KEYWORD in kinds, f"{name} does not accept **kwargs"


def test_map_success_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[Result[Never, object]], Result[Never, None]] = r.map_success(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: Result[Never, None] = mapped(("success", "input"))

    assert output == ("success", None)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


def test_map_success_to_result_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> Result[Never, None]:
        recorded_calls.append((args, kwargs))
        return r.construct_success(None)

    mapped: Callable[[Result[Never, object]], Result[Never, None]] = (
        r.map_success_to_result(
            record_call,
            "extra",  # pyrefly: ignore [bad-argument-count]
            extra_kw="kw",
        )
    )
    output: Result[Never, None] = mapped(("success", "input"))

    assert output == ("success", None)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


def test_tap_success_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[[Result[Never, object]], Result[Never, object]] = r.tap_success(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: Result[Never, object] = tapped(("success", "input"))

    assert output == ("success", "input")
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
