"""Build hook for `pdm-backend`.

Copies the library skill from the project root into the wheel
so that both the source distribution file and the wheel file
contain the skill.
"""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

__docformat__ = "google"


def pdm_build_initialize(  # type: ignore[explicit-any]
    context: Any,  # noqa: ANN401  # pyrefly: ignore[explicit-any]
) -> None:
    """Copy the library skill into the wheel.

    The skill lives at `skills/trcks` in the project root
    (where AI coding agents and CLI tools such as the `skills` CLI
    and `gh skill` discover it).
    For the wheel, it is copied to `trcks/.agents/skills/trcks`
    (where Library Skills discovers it).

    Args:
        context: The build context provided by `pdm-backend`.
    """
    if context.target != "wheel":
        return
    root: Path = context.root
    build_dir: Path = context.build_dir
    _ = shutil.copytree(
        root / "skills" / "trcks",
        build_dir / "trcks" / ".agents" / "skills" / "trcks",
        dirs_exist_ok=True,
    )
