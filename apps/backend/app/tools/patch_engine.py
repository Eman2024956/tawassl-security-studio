import difflib
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


def generate_unified_diff(original_text: str, modified_text: str, filename: str = "target_file") -> str:
    """Generates a standard unified diff between original and modified source code."""
    orig_lines = original_text.splitlines(keepends=True)
    mod_lines = modified_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm=""
    )
    return "".join(diff)


def apply_patch_with_backup(file_path: str, new_content: str) -> Dict[str, Any]:
    """
    Safely writes new content to file_path after creating a timestamped backup (.bak).
    Enforces reviewable and revertible code modifications.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File to patch not found: {file_path}")

    backup_path = path.with_suffix(path.suffix + ".bak")
    original_content = path.read_text(encoding="utf-8", errors="replace")

    # Save backup copy
    shutil.copyfile(path, backup_path)

    # Apply modified code
    path.write_text(new_content, encoding="utf-8")

    diff = generate_unified_diff(original_content, new_content, filename=path.name)

    return {
        "status": "patched",
        "file": str(path),
        "backup": str(backup_path),
        "diff": diff
    }


def revert_patch(file_path: str) -> Dict[str, Any]:
    """Reverts a previously applied patch by restoring its .bak file."""
    path = Path(file_path)
    backup_path = path.with_suffix(path.suffix + ".bak")

    if not backup_path.is_file():
        raise FileNotFoundError(f"No backup file found at: {backup_path}")

    shutil.copyfile(backup_path, path)
    os.remove(backup_path)

    return {
        "status": "reverted",
        "file": str(path)
    }
