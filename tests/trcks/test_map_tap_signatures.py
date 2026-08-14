import inspect
from types import FunctionType
from typing import Final, TypeAlias

import pytest

from trcks.fp._monads import (
    awaitable,
    awaitable_result,
    awaitable_result_tuple,
    awaitable_tuple,
    identity,
    result,
    result_tuple,
    tuple_,
)
from trcks.oop import (
    AwaitableResultTupleWrapper,
    AwaitableResultWrapper,
    AwaitableTupleWrapper,
    AwaitableWrapper,
    ResultTupleWrapper,
    ResultWrapper,
    TupleWrapper,
    Wrapper,
)

CollectedFunctions: TypeAlias = list[tuple[str, FunctionType]]


def _assert_accepts_args_and_kwargs(name: str, function_: FunctionType) -> None:
    kinds = {
        parameter.kind for parameter in inspect.signature(function_).parameters.values()
    }
    assert inspect.Parameter.VAR_POSITIONAL in kinds, f"{name} does not accept *args"
    assert inspect.Parameter.VAR_KEYWORD in kinds, f"{name} does not accept **kwargs"


def _collect_functions() -> CollectedFunctions:
    modules = (
        awaitable,
        awaitable_result,
        awaitable_result_tuple,
        awaitable_tuple,
        identity,
        result,
        result_tuple,
        tuple_,
    )
    return [
        (f"{module.__name__}.{name}", function)
        for module in modules
        for name, function in inspect.getmembers(module, inspect.isfunction)
        if name.startswith(("map", "tap")) and function.__module__ == module.__name__
    ]


def _collect_methods() -> CollectedFunctions:
    classes = (
        Wrapper,
        AwaitableWrapper,
        ResultWrapper,
        TupleWrapper,
        AwaitableTupleWrapper,
        AwaitableResultWrapper,
        ResultTupleWrapper,
        AwaitableResultTupleWrapper,
    )
    return [
        (f"{cls.__qualname__}.{name}", method)
        for cls in classes
        for name, method in inspect.getmembers(cls, inspect.isfunction)
        if name.startswith(("map", "tap"))
    ]


_FUNCTIONS: Final = _collect_functions()
_METHODS: Final = _collect_methods()


@pytest.mark.parametrize(
    ("name", "function"),
    [pytest.param(name, function, id=name) for name, function in _FUNCTIONS],
)
def test_function_forwards_args_and_kwargs(name: str, function: FunctionType) -> None:
    _assert_accepts_args_and_kwargs(name, function)


@pytest.mark.parametrize(
    ("name", "method"),
    [pytest.param(name, method, id=name) for name, method in _METHODS],
)
def test_method_forwards_args_and_kwargs(name: str, method: FunctionType) -> None:
    _assert_accepts_args_and_kwargs(name, method)


def test_more_than_fifty_functions_were_collected() -> None:
    assert len(_FUNCTIONS) > 50  # noqa: PLR2004


def test_more_than_fifty_methods_were_collected() -> None:
    assert len(_METHODS) > 50  # noqa: PLR2004
