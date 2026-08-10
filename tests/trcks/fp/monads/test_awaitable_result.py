from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import AsyncMock, Mock

from trcks import AwaitableResult
from trcks.fp.monads import awaitable_result as ar

_MappedFunction: TypeAlias = Callable[
    [AwaitableResult[object, str]], AwaitableResult[object, str]
]


async def test_map_success_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = ar.map_success(probe, "extra", extra_kw="kw")
    output = await mapped(ar.construct_success("input"))
    assert output == ("success", "mapped")
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


async def test_map_success_to_awaitable_result_forwards_args_and_kwargs() -> None:
    probe = AsyncMock(return_value=("success", "mapped"))
    mapped: _MappedFunction = ar.map_success_to_awaitable_result(
        probe, "extra", extra_kw="kw"
    )
    output = await mapped(ar.construct_success("input"))
    assert output == ("success", "mapped")
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


async def test_tap_success_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = ar.tap_success(probe, "extra", extra_kw="kw")
    output = await tapped(ar.construct_success("input"))
    assert output == ("success", "input")
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
