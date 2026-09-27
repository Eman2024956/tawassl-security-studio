import sys
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class CommandPreset(BaseModel):
    preset_name: str
    executable: str
    allowed_flags: List[str]
    max_args: int = 10
    network_required: bool = False
    timeout_sec: int = 30


# Whitelist of registered command presets
REGISTERED_PRESETS: Dict[str, CommandPreset] = {
    "python_compile": CommandPreset(
        preset_name="python_compile",
        executable=sys.executable,
        allowed_flags=["-m", "py_compile"],
        max_args=4,
        network_required=False,
        timeout_sec=15
    ),
    "ast_inspector": CommandPreset(
        preset_name="ast_inspector",
        executable=sys.executable,
        allowed_flags=["-c"],
        max_args=5,
        network_required=False,
        timeout_sec=15
    )
}


def build_safe_command_args(preset_name: str, target_file: str) -> List[str]:
    """Validates and constructs executable argv without invoking any shell."""
    if preset_name not in REGISTERED_PRESETS:
        raise ValueError(f"Command preset '{preset_name}' is not in registered whitelist.")

    preset = REGISTERED_PRESETS[preset_name]
    if preset_name == "python_compile":
        return [preset.executable, "-m", "py_compile", target_file]
    elif preset_name == "ast_inspector":
        script = (
            "import ast, sys; "
            "src = open(sys.argv[1], 'r', encoding='utf-8').read(); "
            "tree = ast.parse(src); "
            "print('AST_PARSE_OK', len(tree.body))"
        )
        return [preset.executable, "-c", script, target_file]

    raise ValueError(f"Unhandled preset generator for '{preset_name}'")
