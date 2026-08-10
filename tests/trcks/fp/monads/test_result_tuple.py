from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import Mock

from trcks import ResultTuple
from trcks.fp.monads import result_tuple as rt

_MappedFunction: TypeAlias = Callable[
    [ResultTuple[object, str]], ResultTuple[object, str]
]


def test_map_successes_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = rt.map_successes(probe, "extra", extra_kw="kw")
    assert mapped(("success", ("input",))) == ("success", ("mapped",))
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


def test_tap_successes_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = rt.tap_successes(probe, "extra", extra_kw="kw")
    assert tapped(("success", ("input",))) == ("success", ("input",))
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
