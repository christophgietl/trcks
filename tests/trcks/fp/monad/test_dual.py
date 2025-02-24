import sys

from trcks.fp.monad import dual

if sys.version_info >= (3, 11):
    from typing import reveal_type
else:
    from typing_extensions import reveal_type


def test_of_right() -> None:
    dl: dual.Dual[str, int] = dual.of_right(5)
    reveal_type(dl)
    if dl[0] == "left":
        reveal_type(dl)
    else:
        reveal_type(dl)
