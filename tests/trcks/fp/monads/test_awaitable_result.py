from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

import pytest

from trcks.fp.monads import awaitable_result as ar

if TYPE_CHECKING:
    from trcks import Result

_INVALID_RESULT: Final = cast("Result[str, int]", ("neither", 0))


async def test_map_failure_to_awaitable_result_with_invalid_result_raises_type_error() -> (  # noqa: E501
    None
):
    async def _recover(_: str) -> Result[str, int]:
        return ("success", 0)

    invalid_awaitable_result = ar.construct_from_result(_INVALID_RESULT)
    recover = ar.map_failure_to_awaitable_result(_recover)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await recover(invalid_awaitable_result)


async def test_map_success_to_awaitable_result_with_invalid_result_raises_type_error() -> (  # noqa: E501
    None
):
    async def _identity(n: int) -> Result[str, int]:
        return ("success", n)

    invalid_awaitable_result = ar.construct_from_result(_INVALID_RESULT)
    identity = ar.map_success_to_awaitable_result(_identity)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await identity(invalid_awaitable_result)


async def test_tap_failure_to_awaitable_result_with_invalid_side_effect_raises_type_error() -> (  # noqa: E501
    None
):
    async def invalid_side_effect(_: str) -> Result[str, int]:
        return _INVALID_RESULT

    apply_invalid_side_effect_to_failure = ar.tap_failure_to_awaitable_result(
        invalid_side_effect
    )
    awtbl_failure = ar.construct_failure("error")
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await apply_invalid_side_effect_to_failure(awtbl_failure)


async def test_tap_success_to_awaitable_result_with_invalid_side_effect_raises_type_error() -> (  # noqa: E501
    None
):
    async def invalid_side_effect(_: int) -> Result[str, int]:
        return _INVALID_RESULT

    apply_invalid_side_effect_to_success = ar.tap_success_to_awaitable_result(
        invalid_side_effect
    )
    awtbl_success = ar.construct_success(42)
    with pytest.raises(TypeError, match="not a valid Result"):
        _ = await apply_invalid_side_effect_to_success(awtbl_success)
