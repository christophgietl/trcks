"""Build hook for `pdm-backend`."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

__docformat__ = "google"


def pdm_build_initialize(  # type: ignore[explicit-any]
    # `pdm.backend.hooks.base.Context` is not available at type-checking time.
    # Therefore, we need to annotate `context` as `typing.Any`:
    context: Any,  # noqa: ANN401  # pyrefly: ignore[explicit-any]
) -> None:
    """Make the skill available as a library skill by copying it into the wheel."""
    if context.target != "wheel":
        return

    src: Path = context.root / "skills" / "trcks"
    # Library Skills expects the skill to be located in the following directory:
    dst: Path = context.build_dir / "trcks" / ".agents" / "skills" / "trcks"
    _ = shutil.copytree(src, dst, dirs_exist_ok=True)
