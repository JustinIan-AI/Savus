import pytest
from tests.support.mcp_workspace_client import build_client, initialize_client

@pytest.fixture()
def mcp_workspace(tmp_path):
    from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
    from loopdesk.loop_workspace.service import LoopWorkspaceService
    layout = LoopWorkspaceLayout.ensure(tmp_path / "workspace")
    service = LoopWorkspaceService.from_root(layout.root)
    service.ensure_initialized(intent="MCP integration", selected_template="backend-engineer")
    service.record_work_item("work-1", "loop", "Validate MCP handoff.")
    service.set_kill_switch(True)
    service.set_denylist(["dangerous.sh"])
    return layout.root

@pytest.fixture()
def mcp_client(mcp_workspace):
    client = build_client(mcp_workspace)
    print("FIXTURE_INIT_START", flush=True)
    initialize_client(client)
    print("FIXTURE_INIT_END", flush=True)
    yield client
    print("FIXTURE_CLEANUP_START", flush=True)
    process = client.get("process")
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception as exc:
            print("FIXTURE_CLEANUP_ERROR", exc, flush=True)
            process.kill()
    print("FIXTURE_CLEANUP_END", flush=True)

def test_minimal(mcp_client):
    print("TEST_START", flush=True)
    assert True
    print("TEST_END", flush=True)
