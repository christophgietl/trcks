from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from trcks.fp.monads import result as r

if TYPE_CHECKING:
    from trcks import Result


def test_map_failure_to_result_with_invalid_result_raises_type_error() -> None:
    def _identity(_: str) -> Result[str, int]:
        return ("success", 0)

    with pytest.raises(TypeError, match="is not a valid Result"):
        _ = r.map_failure_to_result(_identity)(cast("Result[str, int]", ("neither", 0)))


def test_map_success_to_result_with_invalid_result_raises_type_error() -> None:
    def _identity(x: int) -> Result[str, int]:
        return ("success", x)

    with pytest.raises(TypeError, match="is not a valid Result"):
        _ = r.map_success_to_result(_identity)(cast("Result[str, int]", ("neither", 0)))


def test_tap_failure_to_result_with_invalid_side_effect_raises_type_error() -> None:
    def bad_side_effect(_: str) -> Result[str, int]:
        return cast("Result[str, int]", ("neither", 0))

    tapper = r.tap_failure_to_result(bad_side_effect)
    with pytest.raises(TypeError, match="is not a valid Result"):
        _ = tapper(("failure", "error"))


def test_tap_success_to_result_with_invalid_side_effect_raises_type_error() -> None:
    def bad_side_effect(_: int) -> Result[str, int]:
        return cast("Result[str, int]", ("neither", 0))

    tapper = r.tap_success_to_result(bad_side_effect)
    with pytest.raises(TypeError, match="is not a valid Result"):
        _ = tapper(("success", 42))
