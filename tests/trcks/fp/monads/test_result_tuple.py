from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from trcks.fp.monads import result_tuple as rt

if TYPE_CHECKING:
    import sys
    from collections.abc import Callable

    from trcks import ResultTuple

    if sys.version_info >= (3, 11):
        from typing import Never
    else:
        from typing_extensions import Never

_RecordedCalls: TypeAlias = list[tuple[tuple[object, ...], dict[str, object]]]


def test_map_successes_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    mapped: Callable[[ResultTuple[Never, object]], ResultTuple[Never, None]] = (
        rt.map_successes(
            record_call,
            "extra",  # pyrefly: ignore [bad-argument-count]
            extra_kw="kw",
        )
    )
    output: ResultTuple[Never, None] = mapped(("success", ("input",)))

    assert output == ("success", (None,))
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]


def test_tap_successes_forwards_args_and_kwargs() -> None:
    recorded_calls: _RecordedCalls = []

    def record_call(*args: object, **kwargs: object) -> None:
        recorded_calls.append((args, kwargs))

    tapped: Callable[[ResultTuple[Never, object]], ResultTuple[Never, object]] = (
        rt.tap_successes(
            record_call,
            "extra",  # pyrefly: ignore [bad-argument-count]
            extra_kw="kw",
        )
    )
    output: ResultTuple[Never, object] = tapped(("success", ("input",)))

    assert output == ("success", ("input",))
    assert recorded_calls == [(("input", "extra"), {"extra_kw": "kw"})]
