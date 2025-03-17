from __future__ import annotations

import sys
from collections.abc import Callable

import pytest

from trcks.fp.composition import compose, pipe

if sys.version_info >= (3, 13):
    from typing import assert_type
else:
    from typing_extensions import assert_type


def _foo(x: int) -> str:
    return f"Foo: {x + 1}"


def _incr(x: int) -> int:
    return x + 1


_ZERO_INCRS = ()
_ONE_INCR = (_incr,)
_TWO_INCRS = (_incr, _incr)
_THREE_INCRS = (_incr, _incr, _incr)
_FOUR_INCRS = (_incr, _incr, _incr, _incr)
_FIVE_INCRS = (_incr, _incr, _incr, _incr, _incr)
_SIX_INCRS = (_incr, _incr, _incr, _incr, _incr, _incr)
_SEVEN_INCRS = (_incr, _incr, _incr, _incr, _incr, _incr, _incr)
_EIGHT_INCRS = (_incr, _incr, _incr, _incr, _incr, _incr, _incr, _incr)
_NINE_INCRS = (_incr, _incr, _incr, _incr, _incr, _incr, _incr, _incr, _incr)


def test_compose_correctly_composes_1_function() -> None:
    composed = compose(_ONE_INCR)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_ONE_INCR)


def test_compose_correctly_composes_2_functions() -> None:
    composed = compose(_TWO_INCRS)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_TWO_INCRS)


def test_compose_correctly_composes_3_functions() -> None:
    composed = compose(_THREE_INCRS)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_THREE_INCRS)


def test_compose_correctly_composes_4_functions() -> None:
    composed = compose(_FOUR_INCRS)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_FOUR_INCRS)


def test_compose_correctly_composes_5_functions() -> None:
    composed = compose(_FIVE_INCRS)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_FIVE_INCRS)


def test_compose_correctly_composes_6_functions() -> None:
    composed = compose(_SIX_INCRS)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_SIX_INCRS)


def test_compose_correctly_composes_7_functions() -> None:
    composed = compose(_SEVEN_INCRS)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == len(_SEVEN_INCRS)


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


def test_pipe_correctly_applies_0_functions() -> None:
    piped = pipe((0, *_ZERO_INCRS))
    assert_type(piped, int)
    assert piped == len(_ZERO_INCRS)


def test_pipe_correctly_applies_1_function() -> None:
    piped = pipe((0, *_ONE_INCR))
    assert_type(piped, int)
    assert piped == len(_ONE_INCR)


def test_pipe_correctly_applies_2_functions() -> None:
    piped = pipe((0, *_TWO_INCRS))
    assert_type(piped, int)
    assert piped == len(_TWO_INCRS)


def test_pipe_correctly_applies_3_functions() -> None:
    piped = pipe((0, *_THREE_INCRS))
    assert_type(piped, int)
    assert piped == len(_THREE_INCRS)


def test_pipe_correctly_applies_4_functions() -> None:
    piped = pipe((0, *_FOUR_INCRS))
    assert_type(piped, int)
    assert piped == len(_FOUR_INCRS)


def test_pipe_correctly_applies_5_functions() -> None:
    piped = pipe((0, *_FIVE_INCRS))
    assert_type(piped, int)
    assert piped == len(_FIVE_INCRS)


def test_pipe_correctly_applies_6_functions() -> None:
    piped = pipe((0, *_SIX_INCRS))
    assert_type(piped, int)
    assert piped == len(_SIX_INCRS)


def test_pipe_correctly_applies_7_functions() -> None:
    piped = pipe((0, *_SEVEN_INCRS))
    assert_type(piped, int)
    assert piped == len(_SEVEN_INCRS)


@pytest.mark.parametrize(
    "input_", [42, "test", [4, 5, 6], {"key": "value"}, None, True]
)
def test_pipe_with_1_argument_returns_identical_value(input_: object) -> None:
    output = pipe((input_,))
    assert output is input_


@pytest.mark.parametrize("value", [23, 42, -100, 0, 1000, 999999])
def test_pipe_with_2_arguments_applies_function_to_value(value: int) -> None:
    assert pipe((value, _foo)) == _foo(value)
