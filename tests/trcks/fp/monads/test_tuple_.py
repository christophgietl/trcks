from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import Mock

from trcks.fp.monads import tuple_ as t

_MappedFunction: TypeAlias = Callable[[tuple[str, ...]], tuple[str, ...]]


def test_map_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value="mapped")
    mapped: _MappedFunction = t.map_(probe, "extra", extra_kw="kw")
    assert mapped(("input",)) == ("mapped",)
    probe.assert_called_once_with("input", "extra", extra_kw="kw")


def test_tap_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = t.tap(probe, "extra", extra_kw="kw")
    assert tapped(("input",)) == ("input",)
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
