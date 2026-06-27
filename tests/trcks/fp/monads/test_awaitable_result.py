from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

import pytest

from trcks.fp.monads import awaitable_result as ar

if TYPE_CHECKING:
    from trcks import Result

_INVALID_RESULT: Final = cast("Result[str, int]", ("neither", 0))


async def _make_invalid() -> Result[str, int]:
    return _INVALID_RESULT


async def test_map_failure_to_awaitable_result_with_invalid_result_raises_type_error() -> (  # noqa: E501
    None
):
    async def _recover(_: str) -> Result[str, int]:
        return ("success", 0)

    invalid_awaitable_result = _make_invalid()
    recover = ar.map_failure_to_awaitable_result(_recover)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await recover(invalid_awaitable_result)


async def test_map_success_to_awaitable_result_with_invalid_result_raises_type_error() -> (  # noqa: E501
    None
):
    async def _identity(_: int) -> Result[str, int]:
        return ("success", 0)

    invalid_awaitable_result = _make_invalid()
    identity = ar.map_success_to_awaitable_result(_identity)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await identity(invalid_awaitable_result)


async def test_tap_failure_to_awaitable_result_with_invalid_side_effect_raises_type_error() -> (  # noqa: E501
    None
):
    async def bad_side_effect(_: str) -> Result[str, int]:
        return _INVALID_RESULT

    apply_bad_side_effect_to_failure = ar.tap_failure_to_awaitable_result(
        bad_side_effect
    )
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await apply_bad_side_effect_to_failure(ar.construct_failure("error"))


async def test_tap_success_to_awaitable_result_with_invalid_side_effect_raises_type_error() -> (  # noqa: E501
    None
):
    async def bad_side_effect(_: int) -> Result[str, int]:
        return _INVALID_RESULT

    apply_bad_side_effect_to_success = ar.tap_success_to_awaitable_result(
        bad_side_effect
    )
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await apply_bad_side_effect_to_success(ar.construct_success(42))
