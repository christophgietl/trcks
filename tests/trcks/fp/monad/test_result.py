import sys

from trcks.fp.monad import result

if sys.version_info >= (3, 11):
    from typing import reveal_type
else:
    from typing_extensions import reveal_type


def test_construct_success() -> None:
    rslt: result.Result[str, int] = result.construct_success(5)
    reveal_type(rslt)
    if rslt[0] == "failure":
        reveal_type(rslt)
    else:
        reveal_type(rslt)
