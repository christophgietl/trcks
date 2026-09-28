from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import awaitable_result as ar

if TYPE_CHECKING:
    import sys
    from collections.abc import Callable

    from trcks import AwaitableResult, Result

    if sys.version_info >= (3, 11):
        from typing import Never
    else:
        from typing_extensions import Never

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


async def test_map_success_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[AwaitableResult[Never, object]], AwaitableResult[Never, None]] = (
        ar.map_success(
            record_call,
            "extra",  # pyrefly: ignore [bad-argument-count]
            extra_kw="kw",
        )
    )
    output: Result[Never, None] = await mapped(ar.construct_success("input"))

    assert output == ("success", None)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


async def test_map_success_to_awaitable_result_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    async def record_call(*args: object, **kwargs: object) -> Result[Never, None]:
        recorded_calls.append((args, kwargs))
        return await ar.construct_success(None)

    mapped: Callable[[AwaitableResult[Never, object]], AwaitableResult[Never, None]] = (
        ar.map_success_to_awaitable_result(
            record_call,
            "extra",  # pyrefly: ignore [bad-argument-count]
            extra_kw="kw",
        )
    )
    output: Result[Never, None] = await mapped(ar.construct_success("input"))

    assert output == ("success", None)
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


async def test_tap_success_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[
        [AwaitableResult[Never, object]], AwaitableResult[Never, object]
    ] = ar.tap_success(
        record_call,
        "extra",  # pyrefly: ignore [bad-argument-count]
        extra_kw="kw",
    )
    output: Result[Never, object] = await tapped(ar.construct_success("input"))

    assert output == ("success", "input")
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
