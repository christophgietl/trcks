from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import Mock

from trcks import Result
from trcks.fp.monads import result as r

_MappedFunction: TypeAlias = Callable[[Result[object, str]], Result[object, str]]


def test_map_success_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = r.map_success(probe, "extra", extra_kw="kw")
    assert mapped(("success", "input")) == ("success", "mapped")
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


def test_map_success_to_result_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=("success", "mapped"))
    mapped: _MappedFunction = r.map_success_to_result(probe, "extra", extra_kw="kw")
    assert mapped(("success", "input")) == ("success", "mapped")
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


def test_tap_success_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = r.tap_success(probe, "extra", extra_kw="kw")
    assert tapped(("success", "input")) == ("success", "input")
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
