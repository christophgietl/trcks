from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import Mock

from trcks import AwaitableTuple
from trcks.fp.monads import awaitable_tuple as at

_MappedFunction: TypeAlias = Callable[[AwaitableTuple[str]], AwaitableTuple[str]]


async def test_map_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = at.map_(probe, "extra", extra_kw="kw")
    output = await mapped(at.construct("input"))
    assert output == ("mapped",)
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


async def test_tap_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = at.tap(probe, "extra", extra_kw="kw")
    output = await tapped(at.construct("input"))
    assert output == ("input",)
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
