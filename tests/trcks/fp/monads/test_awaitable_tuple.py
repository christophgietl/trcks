from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import awaitable_tuple as at

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks import AwaitableTuple

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


async def test_map_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[AwaitableTuple[object]], AwaitableTuple[None]] = at.map_(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: tuple[None, ...] = await mapped(at.construct("input"))

    assert output == (None,)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


async def test_tap_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[[AwaitableTuple[object]], AwaitableTuple[object]] = at.tap(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: tuple[object, ...] = await tapped(at.construct("input"))

    assert output == ("input",)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
