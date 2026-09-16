import subprocess
from pathlib import Path

def test_no_opensquilla_in_cli_and_gateway():
    repo_root = Path(__file__).resolve().parents[1]
    res = subprocess.run(
        ["rg", "-i", "opensquilla", "src/loopdesk/cli", "src/loopdesk/gateway"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0, f"Found OpenSquilla in CLI/Gateway: {res.stdout}"

def test_no_squilla_in_cli_tui():
    repo_root = Path(__file__).resolve().parents[1]
    res = subprocess.run(
        ["rg", "-i", "◢ squilla", "src/loopdesk/cli/tui"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0, f"Found '◢ squilla' in CLI TUI: {res.stdout}"
