from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing_extensions import TypeVar, assert_never

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from trcks.types_ import Failure, Result, Success


_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def construct_failure(value: _F) -> Failure[_F]:
    return ("failure", value)


def construct_success(value: _S) -> Success[_S]:
    return ("success", value)


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1]:
        if rslt[0] == "failure":
            return construct_failure(f(rslt[1]))
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return mapped_f


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F2, _S1 | _S2]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1 | _S2]:
        if rslt[0] == "failure":
            return f(rslt[1])
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return mapped_f


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[Result[_F1, _S1]], Result[_F1, _S2]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1, _S2]:
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return construct_success(f(rslt[1]))
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return mapped_f


def map_success_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[Result[_F1, _S1]], Result[_F1 | _F2, _S2]]:
    def mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1 | _F2, _S2]:
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return f(rslt[1])
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return mapped_f


__docformat__ = "google"
