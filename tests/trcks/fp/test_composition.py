from __future__ import annotations

import sys
from typing import Final, TypeAlias, TypeVar

import pytest

from trcks.fp.composition import (
    Composable,
    Composable1,
    Composable2,
    Composable3,
    Composable4,
    Composable5,
    Composable6,
    Composable7,
    Pipeline,
    Pipeline0,
    Pipeline1,
    Pipeline2,
    Pipeline3,
    Pipeline4,
    Pipeline5,
    Pipeline6,
    Pipeline7,
    compose,
    pipe,
)

if sys.version_info >= (3, 13):
    from typing import assert_type
else:
    from typing_extensions import assert_type

_T = TypeVar("_T")

_IntComposable: TypeAlias = Composable[[int], int, int, int, int, int, int, int]
_IntPipeline: TypeAlias = Pipeline[int, int, int, int, int, int, int, int]
_Tuple7: TypeAlias = tuple[_T, _T, _T, _T, _T, _T, _T]
_Tuple8: TypeAlias = tuple[_T, _T, _T, _T, _T, _T, _T, _T]


def _add(a: int, b: int) -> int:
    return a + b


def _double(n: int) -> int:
    return n * 2


def _foo(x: int, /) -> str:
    return f"Foo: {x + 1}"


def _incr(x: int) -> int:
    return x + 1


def _to_output_string(n: int) -> str:
    return f"Output: {n}"


_COMPOSABLES: Final[_Tuple7[_IntComposable]] = (
    (_incr,),
    (_incr, _incr),
    (_incr, _incr, _incr),
    (_incr, _incr, _incr, _incr),
    (_incr, _incr, _incr, _incr, _incr),
    (_incr, _incr, _incr, _incr, _incr, _incr),
    (_incr, _incr, _incr, _incr, _incr, _incr, _incr),
)

_PIPELINES: Final[_Tuple8[_IntPipeline]] = (
    (0,),
    (0, _incr),
    (0, _incr, _incr),
    (0, _incr, _incr, _incr),
    (0, _incr, _incr, _incr, _incr),
    (0, _incr, _incr, _incr, _incr, _incr),
    (0, _incr, _incr, _incr, _incr, _incr, _incr),
    (0, _incr, _incr, _incr, _incr, _incr, _incr, _incr),
)


@pytest.mark.parametrize("composable", _COMPOSABLES)
def test_compose_correctly_composes_composable(composable: _IntComposable) -> None:
    composed = compose(*composable)
    assert composed(0) == len(composable)


def test_compose_correctly_composes_typed_composables() -> None:
    c1: Composable1[[int], int] = (_incr,)
    composed = compose(*c1)
    assert assert_type(composed(0), int) == len(c1)
    c2: Composable2[[int], int, int] = (_incr, _incr)
    composed = compose(*c2)
    assert assert_type(composed(0), int) == len(c2)
    c3: Composable3[[int], int, int, int] = (_incr, _incr, _incr)
    composed = compose(*c3)
    assert assert_type(composed(0), int) == len(c3)
    c4: Composable4[[int], int, int, int, int] = (_incr, _incr, _incr, _incr)
    composed = compose(*c4)
    assert assert_type(composed(0), int) == len(c4)
    c5: Composable5[[int], int, int, int, int, int] = (
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
    )
    composed = compose(*c5)
    assert assert_type(composed(0), int) == len(c5)
    c6: Composable6[[int], int, int, int, int, int, int] = (
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
    )
    composed = compose(*c6)
    assert assert_type(composed(0), int) == len(c6)
    c7: Composable7[[int], int, int, int, int, int, int, int] = (
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
    )
    composed = compose(*c7)
    assert assert_type(composed(0), int) == len(c7)


@pytest.mark.parametrize("value", [23, 42, 100, -1, 0, 1])
def test_compose_with_1_argument_returns_equivalent_function(value: int) -> None:
    composed = compose(_foo)
    assert assert_type(composed(value), str) == _foo(value)


@pytest.mark.parametrize("value", [0, 1, -1, 10, 100, 1000])
def test_compose_with_2_arguments_returns_composed_function(value: int) -> None:
    composed = compose(_foo, len)
    assert assert_type(composed(value), int) == len(_foo(value))


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_multi_arg_first_function(a: int, b: int) -> None:
    composed = compose(_add, _to_output_string)
    assert assert_type(composed(a, b), str) == f"Output: {a + b}"
    assert assert_type(composed(a=a, b=b), str) == f"Output: {a + b}"


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose1_with_multi_arg_function(a: int, b: int) -> None:
    composed = compose(_add)
    assert composed(a, b) == a + b


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose2_with_multi_arg_first_function(a: int, b: int) -> None:
    composed = compose(_add, _double)
    assert composed(a, b) == (a + b) * 2


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose3_with_multi_arg_first_function(a: int, b: int) -> None:
    composed = compose(_add, _double, str)
    assert composed(a, b) == str((a + b) * 2)


@pytest.mark.parametrize("p", _PIPELINES)
def test_pipe_correctly_applies_pipeline(p: _IntPipeline) -> None:
    piped = pipe(*p)
    assert piped == len(p) - 1


def test_pipe_correctly_applies_typed_pipelines() -> None:
    p0: Pipeline0[int] = (0,)
    assert assert_type(pipe(*p0), int) == len(p0) - 1
    p1: Pipeline1[int, int] = (0, _incr)
    assert assert_type(pipe(*p1), int) == len(p1) - 1
    p2: Pipeline2[int, int, int] = (0, _incr, _incr)
    assert assert_type(pipe(*p2), int) == len(p2) - 1
    p3: Pipeline3[int, int, int, int] = (0, _incr, _incr, _incr)
    assert assert_type(pipe(*p3), int) == len(p3) - 1
    p4: Pipeline4[int, int, int, int, int] = (0, _incr, _incr, _incr, _incr)
    assert assert_type(pipe(*p4), int) == len(p4) - 1
    p5: Pipeline5[int, int, int, int, int, int] = (
        0,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
    )
    assert assert_type(pipe(*p5), int) == len(p5) - 1
    p6: Pipeline6[int, int, int, int, int, int, int] = (
        0,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
    )
    assert assert_type(pipe(*p6), int) == len(p6) - 1
    p7: Pipeline7[int, int, int, int, int, int, int, int] = (
        0,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
        _incr,
    )
    assert assert_type(pipe(*p7), int) == len(p7) - 1


@pytest.mark.parametrize(
    "input_", [42, "test", [4, 5, 6], {"key": "value"}, None, True]
)
def test_pipe_with_1_argument_returns_identical_value(input_: object) -> None:
    assert pipe(input_) is input_


@pytest.mark.parametrize("value", [23, 42, -100, 0, 1000, 999999])
def test_pipe_with_2_arguments_applies_function_to_value(value: int) -> None:
    assert pipe(value, _foo) == _foo(value)
