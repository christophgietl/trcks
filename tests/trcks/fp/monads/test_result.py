from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

import pytest

from trcks.fp.monads import result as r

if TYPE_CHECKING:
    from trcks import Result

_INVALID_RESULT: Final = cast("Result[str, int]", ("neither", 0))


def test_map_failure_to_result_with_invalid_result_raises_type_error() -> None:
    recover = r.map_failure_to_result(lambda _: ("success", 0))
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = recover(_INVALID_RESULT)


def test_map_success_to_result_with_invalid_result_raises_type_error() -> None:
    identity = r.map_success_to_result(lambda x: ("success", x))
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = identity(_INVALID_RESULT)


def test_tap_failure_to_result_with_invalid_side_effect_raises_type_error() -> None:
    apply_bad_side_effect = r.tap_failure_to_result(lambda _: _INVALID_RESULT)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = apply_bad_side_effect(("failure", "error"))


def test_tap_success_to_result_with_invalid_side_effect_raises_type_error() -> None:
    apply_bad_side_effect = r.tap_success_to_result(lambda _: _INVALID_RESULT)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = apply_bad_side_effect(("success", 42))
