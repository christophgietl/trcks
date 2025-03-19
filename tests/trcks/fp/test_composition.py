from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TypeVar

import pytest

from trcks.fp.composition import Composable, Pipeline, compose, pipe

if sys.version_info >= (3, 13):
    from typing import assert_type
else:
    from typing_extensions import assert_type

if sys.version_info >= (3, 11):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_T = TypeVar("_T")

_IntComposable: TypeAlias = Composable[int, int, int, int, int, int, int, int]
_IntPipeline: TypeAlias = Pipeline[int, int, int, int, int, int, int, int]
_Tuple7: TypeAlias = tuple[_T, _T, _T, _T, _T, _T, _T]
_Tuple8: TypeAlias = tuple[_T, _T, _T, _T, _T, _T, _T, _T]


def _foo(x: int) -> str:
    return f"Foo: {x + 1}"


def _incr(x: int) -> int:
    return x + 1


_COMPOSABLES: _Tuple7[_IntComposable] = (
    (_incr,),
    (_incr, _incr),
    (_incr, _incr, _incr),
    (_incr, _incr, _incr, _incr),
    (_incr, _incr, _incr, _incr, _incr),
    (_incr, _incr, _incr, _incr, _incr, _incr),
    (_incr, _incr, _incr, _incr, _incr, _incr, _incr),
)

_PIPELINES: _Tuple8[_IntPipeline] = (
    (0,),
    (0, *_COMPOSABLES[0]),
    (0, *_COMPOSABLES[1]),
    (0, *_COMPOSABLES[2]),
    (0, *_COMPOSABLES[3]),
    (0, *_COMPOSABLES[4]),
    (0, *_COMPOSABLES[5]),
    (0, *_COMPOSABLES[6]),
)


@pytest.mark.parametrize("composable", _COMPOSABLES)
def test_compose_correctly_composes_composable(composable: _IntComposable) -> None:
    composed = compose(composable)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(composable)


@pytest.mark.parametrize("value", [23, 42, 100, -1, 0, 1])
def test_compose_with_1_argument_returns_equivalent_function(value: int) -> None:
    composed = compose((_foo,))
    assert_type(composed, Callable[[int], str])
    assert composed(value) == _foo(value)


@pytest.mark.parametrize("value", [0, 1, -1, 10, 100, 1000])
def test_compose_with_2_arguments_returns_composed_function(value: int) -> None:
    composed = compose((_foo, len))
    assert_type(composed, Callable[[int], int])
    assert composed(value) == len(_foo(value))


@pytest.mark.parametrize("p", _PIPELINES)
def test_pipe_correctly_applies_pipeline(p: _IntPipeline) -> None:
    piped = pipe(p)
    assert_type(piped, int)
    assert piped == len(p) - 1


@pytest.mark.parametrize(
    "input_", [42, "test", [4, 5, 6], {"key": "value"}, None, True]
)
def test_pipe_with_1_argument_returns_identical_value(input_: object) -> None:
    assert pipe((input_,)) is input_


@pytest.mark.parametrize("value", [23, 42, -100, 0, 1000, 999999])
def test_pipe_with_2_arguments_applies_function_to_value(value: int) -> None:
    assert pipe((value, _foo)) == _foo(value)
