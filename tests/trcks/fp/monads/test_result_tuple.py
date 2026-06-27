from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

import pytest

from trcks.fp.monads import result_tuple as rt

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks import ResultTuple

_INVALID_RESULT_TUPLE: Final = cast("ResultTuple[str, int]", ("neither", ()))


def test_map_failure_with_invalid_result_tuple_raises_type_error() -> None:
    recover: Callable[[ResultTuple[str, int]], ResultTuple[str, int]] = (
        rt.map_failure_to_iterable(lambda _: [0])
    )
    with pytest.raises(TypeError, match="not a valid ResultTuple"):
        _ = recover(_INVALID_RESULT_TUPLE)


def test_map_successes_with_invalid_inner_result_raises_type_error() -> None:
    map_successes_to_invalid_result_tuple: Callable[
        [ResultTuple[str, int]], ResultTuple[str, int]
    ] = rt.map_successes_to_result_iterable(lambda _: _INVALID_RESULT_TUPLE)
    with pytest.raises(TypeError, match="not a valid ResultIterable"):
        _ = map_successes_to_invalid_result_tuple(("success", (1,)))


def test_map_successes_with_invalid_result_tuple_raises_type_error() -> None:
    identity: Callable[[ResultTuple[str, int]], ResultTuple[str, int]] = (
        rt.map_successes_to_result_iterable(lambda x: ("success", (x,)))
    )
    with pytest.raises(TypeError, match="not a valid ResultTuple"):
        _ = identity(_INVALID_RESULT_TUPLE)


def test_tap_successes_with_invalid_inner_result_raises_type_error() -> None:
    invalid_side_effect: Callable[[ResultTuple[str, int]], ResultTuple[str, int]] = (
        rt.tap_successes_to_result_iterable(lambda _: _INVALID_RESULT_TUPLE)
    )
    with pytest.raises(TypeError, match="not a valid ResultIterable"):
        _ = invalid_side_effect(("success", (1,)))
