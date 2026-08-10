from collections.abc import Callable
from typing import TypeAlias
from unittest.mock import Mock

from trcks.fp.monads import identity as i

_MappedFunction: TypeAlias = Callable[[str], str]


def test_tap_forwards_args_and_kwargs() -> None:
    probe = Mock(return_value=None)
    tapped: _MappedFunction = i.tap(probe, "extra", extra_kw="kw")
    output = tapped("input")
    assert output == "input"
    probe.assert_called_once_with("input", "extra", extra_kw="kw")
