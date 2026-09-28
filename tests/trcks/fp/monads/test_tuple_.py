from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import tuple_ as t

if TYPE_CHECKING:
    from collections.abc import Callable

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


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
