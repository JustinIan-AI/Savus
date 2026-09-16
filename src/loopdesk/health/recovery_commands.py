from __future__ import annotations

import shlex
from pathlib import Path

CONFIG_AWARE_COMMAND_PREFIXES = (
    "loopdesk gateway restart",
    "loopdesk gateway start",
    "loopdesk gateway status",
    "loopdesk providers configure",
    "loopdesk providers status",
    "loopdesk config ",
    "loopdesk search status",
    "loopdesk search configure",
    "loopdesk diagnostics status",
    "loopdesk memory status",
    "loopdesk memory repair list",
    "loopdesk memory repair run",
    "loopdesk configure ",
    "loopdesk onboard",
    "loopdesk sandbox ",
    "loopdesk channels add",
    "loopdesk channels edit",
    "loopdesk channels enable",
    "loopdesk channels disable",
    "loopdesk channels remove",
    "loopdesk channels list",
    "loopdesk channels restart",
    "loopdesk channels status",
)


def supports_config_option(command: str) -> bool:
    return any(command.startswith(prefix) for prefix in CONFIG_AWARE_COMMAND_PREFIXES)


def command_with_config(command: str, config_path: str | Path | None) -> str:
    if not config_path or " --config " in command or not supports_config_option(command):
        return command
    return f"{command} --config {shlex.quote(str(config_path))}"
