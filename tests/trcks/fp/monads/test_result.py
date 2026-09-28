from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import result as r

if TYPE_CHECKING:
    import sys
    from collections.abc import Callable

    from trcks import Result

    if sys.version_info >= (3, 11):
        from typing import Never
    else:
        from typing_extensions import Never

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


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
