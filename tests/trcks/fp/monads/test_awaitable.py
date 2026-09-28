from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import awaitable as a

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


async def test_map_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[Awaitable[object]], Awaitable[None]] = a.map_(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: None = await mapped(a.construct("input"))  # type: ignore[func-returns-value]

    assert output is None
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


async def test_map_to_awaitable_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    async def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[Awaitable[object]], Awaitable[None]] = a.map_to_awaitable(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: None = await mapped(a.construct("input"))  # type: ignore[func-returns-value]

    assert output is None
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


async def test_tap_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[[Awaitable[object]], Awaitable[object]] = a.tap(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: object = await tapped(a.construct("input"))

    assert output == "input"
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
