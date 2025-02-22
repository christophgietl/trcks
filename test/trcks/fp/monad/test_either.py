import sys

from trcks.fp.monad import either

if sys.version_info >= (3, 11):
    from typing import reveal_type
else:
    from typing_extensions import reveal_type


def test_of_right() -> None:
    ethr: either.Either[str, int] = either.of_right(5)
    reveal_type(ethr)
    if ethr.track == "left":
        reveal_type(ethr)
    else:
        reveal_type(ethr)
