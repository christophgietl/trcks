"""Build hook for `pdm-backend`."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

__docformat__ = "google"


class _Context(Protocol):
    """Replacement for `pdm.backend.hooks.base.Context`.

    Note:
        The package `pdm-backend` is not available during type-checking.
    """

    @property
    def build_dir(self) -> Path: ...

    @property
    def root(self) -> Path: ...

    @property
    def target(self) -> str: ...


def pdm_build_initialize(context: _Context) -> None:
    """Make the skill available as a library skill by copying it into the wheel."""
    if context.target != "wheel":
        return

    src = context.root / "skills" / "trcks"
    # Library Skills expects the skill to be located in this directory:
    dst = context.build_dir / "trcks" / ".agents" / "skills" / "trcks"
    _ = shutil.copytree(src, dst, dirs_exist_ok=True)
