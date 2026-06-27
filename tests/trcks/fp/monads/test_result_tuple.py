from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

import pytest

from trcks.fp.monads import result_tuple as rt

if TYPE_CHECKING:
    from trcks import ResultTuple

_INVALID_RESULT_TUPLE: Final = cast("ResultTuple[str, int]", ("neither", ()))


def test_map_failure_to_iterable_with_invalid_result_tuple_raises_type_error() -> None:
    with pytest.raises(TypeError, match="not a valid ResultTuple"):
        _ = rt.map_failure_to_iterable(lambda x: [x])(_INVALID_RESULT_TUPLE)


def test_map_successes_to_result_iterable_with_invalid_inner_result_raises_type_error() -> (  # noqa: E501
    None
):
    mapper = rt.map_successes_to_result_iterable(
        lambda _: cast("ResultTuple[str, str]", ("neither", ()))
    )
    with pytest.raises(TypeError, match="not a valid ResultIterable"):
        _ = mapper(("success", (1,)))


def test_map_successes_to_result_iterable_with_invalid_result_tuple_raises_type_error() -> (  # noqa: E501
    None
):
    with pytest.raises(TypeError, match="not a valid ResultTuple"):
        _ = rt.map_successes_to_result_iterable(lambda x: ("success", (x,)))(
            _INVALID_RESULT_TUPLE
        )


def test_tap_successes_to_result_iterable_with_invalid_inner_result_raises_type_error() -> (  # noqa: E501
    None
):
    apply_bad_side_effect = rt.tap_successes_to_result_iterable(
        lambda _: cast("ResultTuple[str, object]", ("neither", ()))
    )
    with pytest.raises(TypeError, match="not a valid ResultIterable"):
        _ = apply_bad_side_effect(("success", (1,)))
