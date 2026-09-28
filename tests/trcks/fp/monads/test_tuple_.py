from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Final, TypeAlias

import pytest

from trcks.fp.monads import tuple_ as t

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from types import FunctionType

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]

_MAP_AND_TAP_FUNCTIONS: Final[Mapping[str, FunctionType]] = {
    name: function
    for name, function in inspect.getmembers(t, inspect.isfunction)
    if name.startswith(("map", "tap"))
}


def test_collected_many_map_and_tap_functions() -> None:
    assert len(_MAP_AND_TAP_FUNCTIONS) > 20  # noqa: PLR2004


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


def test_map_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[tuple[object, ...]], tuple[None, ...]] = t.map_(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: tuple[None, ...] = mapped(("input",))

    assert output == (None,)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


def test_tap_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[[tuple[object, ...]], tuple[object, ...]] = t.tap(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: tuple[object, ...] = tapped(("input",))

    assert output == ("input",)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
