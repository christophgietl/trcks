from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import Mock

from trcks import AwaitableResultTuple
from trcks.fp.monads import awaitable_result_tuple as art

_MappedFunction: TypeAlias = Callable[
    [AwaitableResultTuple[object, str]], AwaitableResultTuple[object, str]
]


async def test_map_successes_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = art.map_successes(probe, "extra", extra_kw="kw")
    output = await mapped(art.construct_successes("input"))
    assert output == ("success", ("mapped",))
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


async def test_tap_successes_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = art.tap_successes(probe, "extra", extra_kw="kw")
    output = await tapped(art.construct_successes("input"))
    assert output == ("success", ("input",))
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
