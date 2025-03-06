from collections.abc import Awaitable
from typing import Literal, Union

from trcks._typing_extensions import Never, TypeAlias, TypeVar

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


Failure: TypeAlias = tuple[Literal["failure"], _F_co]
Success: TypeAlias = tuple[Literal["success"], _S_co]
Result: TypeAlias = Union[Failure[_F_co], Success[_S_co]]


AwaitableFailure: TypeAlias = Awaitable[Failure[_F_co]]
AwaitableSuccess: TypeAlias = Awaitable[Success[_S_co]]
AwaitableResult: TypeAlias = Awaitable[Result[_F_co, _S_co]]
