from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from trcks.fp.monads import result_tuple as rt

if TYPE_CHECKING:
    from trcks import ResultTuple


def test_map_failure_to_iterable_with_invalid_result_tuple_raises_type_error() -> None:
    def _to_list(x: str) -> list[str]:
        return [x]

    with pytest.raises(TypeError, match="is not a valid ResultTuple"):
        _ = rt.map_failure_to_iterable(_to_list)(
            cast("ResultTuple[str, int]", ("neither", ()))
        )


def test_map_successes_to_result_iterable_with_invalid_inner_result_raises_type_error() -> (  # noqa: E501
    None
):
    def bad_f(_: int) -> ResultTuple[str, str]:
        return cast("ResultTuple[str, str]", ("neither", ()))

    mapper = rt.map_successes_to_result_iterable(bad_f)
    with pytest.raises(TypeError, match="is not a valid ResultIterable"):
        _ = mapper(("success", (1,)))


def test_map_successes_to_result_iterable_with_invalid_result_tuple_raises_type_error() -> (  # noqa: E501
    None
):
    def _to_tuple(x: int) -> ResultTuple[str, int]:
        return ("success", (x,))

    with pytest.raises(TypeError, match="is not a valid ResultTuple"):
        _ = rt.map_successes_to_result_iterable(_to_tuple)(
            cast("ResultTuple[str, int]", ("neither", ()))
        )


def test_tap_successes_to_result_iterable_with_invalid_inner_result_raises_type_error() -> (  # noqa: E501
    None
):
    def bad_f(_: int) -> ResultTuple[str, object]:
        return cast("ResultTuple[str, object]", ("neither", ()))

    tapper = rt.tap_successes_to_result_iterable(bad_f)
    with pytest.raises(TypeError, match="is not a valid ResultIterable"):
        _ = tapper(("success", (1,)))
