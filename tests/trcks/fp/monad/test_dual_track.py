import sys

from trcks.fp.monad import dual_track

if sys.version_info >= (3, 11):
    from typing import reveal_type
else:
    from typing_extensions import reveal_type


def test_of_right() -> None:
    ethr: dual_track.DualTrack[str, int] = dual_track.of_right(5)
    reveal_type(ethr)
    if ethr[0] == "left":
        reveal_type(ethr)
    else:
        reveal_type(ethr)
