from collections.abc import Awaitable, Callable
from typing import TypeAlias
from unittest.mock import AsyncMock, Mock

from trcks.fp.monads import awaitable as a

_MappedFunction: TypeAlias = Callable[[Awaitable[str]], Awaitable[str]]


async def test_map_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = a.map_(probe, "extra", extra_kw="kw")
    output = await mapped(a.construct("input"))
    assert output == "mapped"
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


async def test_map_to_awaitable_forwards_args_and_kwargs() -> None:
    probe = AsyncMock(return_value="mapped")
    mapped: _MappedFunction = a.map_to_awaitable(probe, "extra", extra_kw="kw")
    output = await mapped(a.construct("input"))
    assert output == "mapped"
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


async def test_tap_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = a.tap(probe, "extra", extra_kw="kw")
    output = await tapped(a.construct("input"))
    assert output == "input"
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
