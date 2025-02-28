import sys
from collections.abc import Callable

import pytest

from trcks.fp.composition import compose, pipe

if sys.version_info >= (3, 11):
    from typing import assert_type
else:
    from typing_extensions import assert_type

_REPETITIONS = [1, 2, 3, 4, 5, 10, 20, 100]


@pytest.mark.parametrize("input_", [1, "a", [1, 2, 3], {"a": 1}])
def test_compose_without_arguments_returns_identity_function(input_: object) -> None:
    func: Callable[[object], object] = compose()
    output = func(input_)
    assert output is input_


@pytest.mark.parametrize("value", [23, 42, 100, -1, 0, 1])
def test_compose_with_one_argument_returns_equivalent_function(value: int) -> None:
    def foo(x: int) -> str:
        return f"Foo: {x + 1}"

    composed_foo = compose(foo)
    assert_type(composed_foo, Callable[[int], str])
    assert composed_foo(value) == foo(value)


@pytest.mark.parametrize("value", [0, 1, -1, 10, 100, 1000])
def test_compose_with_two_arguments_returns_composed_function(value: int) -> None:
    def foo(x: int) -> str:
        return f"Foo: {x + 1}"

    def bar(x: str) -> int:
        return len(x)

    foo_then_bar = compose(foo, bar)
    assert_type(foo_then_bar, Callable[[int], int])
    assert foo_then_bar(value) == bar(foo(value))


@pytest.mark.parametrize("repetitions", _REPETITIONS)
def test_compose_correctly_composes_many_functions(repetitions: int) -> None:
    def incr(x: int) -> int:
        return x + 1

    functions = (incr,) * repetitions
    composed = compose(*functions)
    assert_type(composed, Callable[[int], int])
    assert composed(0) == repetitions


@pytest.mark.parametrize(
    "input_", [42, "test", [4, 5, 6], {"key": "value"}, None, True]
)
def test_pipe_with_one_argument_returns_identical_value(input_: object) -> None:
    output = pipe(input_)
    assert output is input_


@pytest.mark.parametrize("value", [23, 42, -100, 0, 1000, 999999])
def test_pipe_with_two_arguments_applies_function_to_value(value: int) -> None:
    def foo(x: int) -> str:
        return f"Foo: {x + 1}"

    assert pipe(value, foo) == foo(value)


@pytest.mark.parametrize("repetitions", _REPETITIONS)
def test_pipe_correctly_applies_many_functions(repetitions: int) -> None:
    def incr(x: int) -> int:
        return x + 1

    functions = (incr,) * repetitions
    piped = pipe(0, *functions)
    assert_type(piped, int)
    assert piped == repetitions
