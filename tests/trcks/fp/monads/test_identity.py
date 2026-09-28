from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import identity as i

if TYPE_CHECKING:
    from collections.abc import Callable

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


def test_tap_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[[object], object] = i.tap(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: object = tapped("input")

    assert output == "input"
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
