"""Build hook for `pdm-backend`.

See:
    https://github.com/pdm-project/pdm-backend/blob/2.4.9/docs/hooks.md
"""

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

    def ensure_build_dir(self) -> Path: ...

    @property
    def root(self) -> Path: ...

    @property
    def target(self) -> str: ...


def _copy_skill_to_build_dir(*, root: Path, build_dir: Path) -> None:
    src = root / "skills" / "trcks"
    # Library Skills expects the skill in this directory:
    dst = build_dir / "trcks" / ".agents" / "skills" / "trcks"
    _ = shutil.copytree(src, dst, dirs_exist_ok=True)


def pdm_build_hook_enabled(context: _Context) -> bool:
    """Only for wheel builds."""
    return context.target == "wheel"


def pdm_build_initialize(context: _Context) -> None:
    """Make the skill available as a library skill by copying it into the wheel."""
    build_dir = context.ensure_build_dir()
    _copy_skill_to_build_dir(root=context.root, build_dir=build_dir)
