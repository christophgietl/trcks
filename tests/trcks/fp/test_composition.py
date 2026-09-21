from __future__ import annotations

from typing import TYPE_CHECKING, Final, Protocol, TypeVar

import pytest

from trcks.fp.composition import (
    Composable1,
    Composable2,
    Composable3,
    Composable4,
    Composable5,
    Composable6,
    Composable7,
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

if TYPE_CHECKING:
    from collections.abc import Callable

_T_co = TypeVar("_T_co", covariant=True)


_INTEGERS: Final[tuple[int, ...]] = (23, 42, -100, 0, 1000, 999999)


class _MapAddInput(Protocol[_T_co]):
    def __call__(self, a: int, b: int) -> _T_co: ...


def _add(a: int, b: int) -> int:
    return a + b


def _double(n: int) -> int:
    return n * 2


def _foo(x: int, /) -> str:
    return f"Foo: {x + 1}"


def _to_output_string(n: int) -> str:
    return f"Output: {n}"


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_1_complex_argument_correctly_composes_function(
    a: int, b: int
) -> None:
    composed: _MapAddInput[int] = compose(_add)
    assert composed(a, b) == _add(a, b)
    assert composed(a=a, b=b) == _add(a=a, b=b)


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_1_simple_argument_correctly_composes_function(
    input_: int,
) -> None:
    composed: Callable[[int], str] = compose(_foo)
    assert composed(input_) == _foo(input_)


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_2_complex_arguments_correctly_composes_functions(
    a: int, b: int
) -> None:
    composed: _MapAddInput[int] = compose(_add, _double)
    assert composed(a, b) == _double(_add(a, b))
    assert composed(a=a, b=b) == _double(_add(a=a, b=b))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_2_simple_arguments_correctly_composes_functions(
    input_: int,
) -> None:
    composed: Callable[[int], int] = compose(_foo, len)
    assert composed(input_) == len(_foo(input_))


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_3_complex_arguments_correctly_composes_functions(
    a: int, b: int
) -> None:
    composed: _MapAddInput[str] = compose(_add, _double, str)
    assert composed(a, b) == str(_double(_add(a, b)))
    assert composed(a=a, b=b) == str(_double(_add(a=a, b=b)))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_3_simple_arguments_correctly_composes_functions(
    input_: int,
) -> None:
    composed: Callable[[int], str] = compose(_foo, len, _to_output_string)
    assert composed(input_) == _to_output_string(len(_foo(input_)))


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_4_complex_arguments_correctly_composes_functions(
    a: int, b: int
) -> None:
    composed: _MapAddInput[int] = compose(_add, _double, str, len)
    assert composed(a, b) == len(str(_double(_add(a, b))))
    assert composed(a=a, b=b) == len(str(_double(_add(a=a, b=b))))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_4_simple_arguments_correctly_composes_functions(
    input_: int,
) -> None:
    composed: Callable[[int], int] = compose(_foo, len, _to_output_string, len)
    assert composed(input_) == len(_to_output_string(len(_foo(input_))))


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_5_complex_arguments_correctly_composes_functions(
    a: int, b: int
) -> None:
    composed: _MapAddInput[str] = compose(_add, _double, str, len, _to_output_string)
    assert composed(a, b) == _to_output_string(len(str(_double(_add(a, b)))))
    assert composed(a=a, b=b) == _to_output_string(len(str(_double(_add(a=a, b=b)))))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_5_simple_arguments_correctly_composes_functions(
    input_: int,
) -> None:
    composed: Callable[[int], str] = compose(
        _foo, len, _to_output_string, len, _to_output_string
    )
    assert composed(input_) == _to_output_string(
        len(_to_output_string(len(_foo(input_))))
    )


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_6_complex_arguments_correctly_composes_functions(
    a: int, b: int
) -> None:
    composed: _MapAddInput[int] = compose(
        _add, _double, str, len, _to_output_string, len
    )
    assert composed(a, b) == len(_to_output_string(len(str(_double(_add(a, b))))))
    assert composed(a=a, b=b) == len(
        _to_output_string(len(str(_double(_add(a=a, b=b)))))
    )


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_6_simple_arguments_correctly_composes_functions(
    input_: int,
) -> None:
    composed: Callable[[int], int] = compose(
        _foo, len, _to_output_string, len, _to_output_string, len
    )
    assert composed(input_) == len(
        _to_output_string(len(_to_output_string(len(_foo(input_)))))
    )


@pytest.mark.parametrize(("a", "b"), [(2, 3), (5, 7), (10, 20)])
def test_compose_with_7_complex_arguments_correctly_composes_functions(
    a: int, b: int
) -> None:
    composed: _MapAddInput[str] = compose(
        _add, _double, str, len, _to_output_string, len, _to_output_string
    )
    assert composed(a, b) == _to_output_string(
        len(_to_output_string(len(str(_double(_add(a, b))))))
    )
    assert composed(a=a, b=b) == _to_output_string(
        len(_to_output_string(len(str(_double(_add(a=a, b=b))))))
    )


@pytest.mark.parametrize("input_", _INTEGERS)
def test_compose_with_7_simple_arguments_correctly_composes_functions(
    input_: int,
) -> None:
    composed: Callable[[int], str] = compose(
        _foo,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
        _to_output_string,
    )
    assert composed(input_) == _to_output_string(
        len(_to_output_string(len(_to_output_string(len(_foo(input_))))))
    )


def test_compose_with_variadic_composable1_argument_correctly_composes_function() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable1[[dict[str, str]], int] = (len,)
    composed: Callable[[dict[str, str]], int] = compose(*composable)
    assert composed(input_) == len(input_)


def test_compose_with_variadic_composable2_argument_correctly_composes_functions() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable2[[dict[str, str]], int, str] = (len, _to_output_string)
    composed: Callable[[dict[str, str]], str] = compose(*composable)
    assert composed(input_) == _to_output_string(len(input_))


def test_compose_with_variadic_composable3_argument_correctly_composes_functions() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable3[[dict[str, str]], int, str, int] = (
        len,
        _to_output_string,
        len,
    )
    composed: Callable[[dict[str, str]], int] = compose(*composable)
    assert composed(input_) == len(_to_output_string(len(input_)))


def test_compose_with_variadic_composable4_argument_correctly_composes_functions() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable4[[dict[str, str]], int, str, int, str] = (
        len,
        _to_output_string,
        len,
        _to_output_string,
    )
    composed: Callable[[dict[str, str]], str] = compose(*composable)
    assert composed(input_) == _to_output_string(len(_to_output_string(len(input_))))


def test_compose_with_variadic_composable5_argument_correctly_composes_functions() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable5[[dict[str, str]], int, str, int, str, int] = (
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
    )
    composed: Callable[[dict[str, str]], int] = compose(*composable)
    assert composed(input_) == len(
        _to_output_string(len(_to_output_string(len(input_))))
    )


def test_compose_with_variadic_composable6_argument_correctly_composes_functions() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable6[[dict[str, str]], int, str, int, str, int, str] = (
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
        _to_output_string,
    )
    composed: Callable[[dict[str, str]], str] = compose(*composable)
    assert composed(input_) == _to_output_string(
        len(_to_output_string(len(_to_output_string(len(input_)))))
    )


def test_compose_with_variadic_composable7_argument_correctly_composes_functions() -> (
    None
):
    input_: dict[str, str] = {"key": "value"}
    composable: Composable7[[dict[str, str]], int, str, int, str, int, str, int] = (
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
    )
    composed: Callable[[dict[str, str]], int] = compose(*composable)
    assert composed(input_) == len(
        _to_output_string(len(_to_output_string(len(_to_output_string(len(input_))))))
    )


def test_pipe_with_1_positional_argument_returns_identical_bool() -> None:
    input_: bool = True
    output: bool = pipe(input_)
    assert output is input_


def test_pipe_with_1_positional_argument_returns_identical_dict() -> None:
    input_: dict[str, str] = {"key": "value"}
    output: dict[str, str] = pipe(input_)
    assert output is input_


def test_pipe_with_1_positional_argument_returns_identical_int() -> None:
    input_: int = 42
    output: int = pipe(input_)
    assert output is input_


def test_pipe_with_1_positional_argument_returns_identical_list() -> None:
    input_: list[int] = [4, 5, 6]
    output: list[int] = pipe(input_)
    assert output is input_


def test_pipe_with_1_positional_argument_returns_identical_none() -> None:
    input_: None = None
    output: None = pipe(input_)
    assert output is input_


def test_pipe_with_1_positional_argument_returns_identical_str() -> None:
    input_: str = "test"
    output: str = pipe(input_)
    assert output is input_


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_2_positional_arguments_correctly_applies_function(
    input_: int,
) -> None:
    output: str = pipe(input_, _foo)
    assert output == _foo(input_)


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_3_positional_arguments_correctly_applies_functions(
    input_: int,
) -> None:
    output: int = pipe(input_, _foo, len)
    assert output == len(_foo(input_))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_4_positional_arguments_correctly_applies_functions(
    input_: int,
) -> None:
    output: str = pipe(input_, _foo, len, _to_output_string)
    assert output == _to_output_string(len(_foo(input_)))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_5_positional_arguments_correctly_applies_functions(
    input_: int,
) -> None:
    output: int = pipe(input_, _foo, len, _to_output_string, len)
    assert output == len(_to_output_string(len(_foo(input_))))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_6_positional_arguments_correctly_applies_functions(
    input_: int,
) -> None:
    output: str = pipe(input_, _foo, len, _to_output_string, len, _to_output_string)
    assert output == _to_output_string(len(_to_output_string(len(_foo(input_)))))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_7_positional_arguments_correctly_applies_functions(
    input_: int,
) -> None:
    output: int = pipe(
        input_, _foo, len, _to_output_string, len, _to_output_string, len
    )
    assert output == len(_to_output_string(len(_to_output_string(len(_foo(input_))))))


@pytest.mark.parametrize("input_", _INTEGERS)
def test_pipe_with_8_positional_arguments_correctly_applies_functions(
    input_: int,
) -> None:
    output: str = pipe(
        input_,
        _foo,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
        _to_output_string,
    )
    assert output == _to_output_string(
        len(_to_output_string(len(_to_output_string(len(_foo(input_))))))
    )


def test_pipe_with_variadic_pipeline0_argument_returns_identical_dict() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline0[dict[str, str]] = (input_,)
    output: dict[str, str] = pipe(*pipeline)
    assert output is input_


def test_pipe_with_variadic_pipeline1_argument_correctly_applies_function() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline1[dict[str, str], int] = (input_, len)
    output: int = pipe(*pipeline)
    assert output == len(input_)


def test_pipe_with_variadic_pipeline2_argument_correctly_applies_functions() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline2[dict[str, str], int, str] = (input_, len, _to_output_string)
    output: str = pipe(*pipeline)
    assert output == _to_output_string(len(input_))


def test_pipe_with_variadic_pipeline3_argument_correctly_applies_functions() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline3[dict[str, str], int, str, int] = (
        input_,
        len,
        _to_output_string,
        len,
    )
    output: int = pipe(*pipeline)
    assert output == len(_to_output_string(len(input_)))


def test_pipe_with_variadic_pipeline4_argument_correctly_applies_functions() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline4[dict[str, str], int, str, int, str] = (
        input_,
        len,
        _to_output_string,
        len,
        _to_output_string,
    )
    output: str = pipe(*pipeline)
    assert output == _to_output_string(len(_to_output_string(len(input_))))


def test_pipe_with_variadic_pipeline5_argument_correctly_applies_functions() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline5[dict[str, str], int, str, int, str, int] = (
        input_,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
    )
    output: int = pipe(*pipeline)
    assert output == len(_to_output_string(len(_to_output_string(len(input_)))))


def test_pipe_with_variadic_pipeline6_argument_correctly_applies_functions() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline6[dict[str, str], int, str, int, str, int, str] = (
        input_,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
        _to_output_string,
    )
    output: str = pipe(*pipeline)
    assert output == _to_output_string(
        len(_to_output_string(len(_to_output_string(len(input_)))))
    )


def test_pipe_with_variadic_pipeline7_argument_correctly_applies_functions() -> None:
    input_: dict[str, str] = {"key": "value"}
    pipeline: Pipeline7[dict[str, str], int, str, int, str, int, str, int] = (
        input_,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
        _to_output_string,
        len,
    )
    output: int = pipe(*pipeline)
    assert output == len(
        _to_output_string(len(_to_output_string(len(_to_output_string(len(input_))))))
    )
