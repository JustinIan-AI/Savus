from __future__ import annotations

import pytest
from loopdesk.connectors.task_source import TaskSourceAdapter, RemoteTask, SyncDirection

class MockJiraAdapter(TaskSourceAdapter):
    def __init__(self) -> None:
        self.remote_db: dict[str, RemoteTask] = {}

    def fetch_task(self, remote_id: str) -> RemoteTask | None:
        return self.remote_db.get(remote_id)

    def update_task_status(self, remote_id: str, status: str) -> bool:
        if remote_id in self.remote_db:
            self.remote_db[remote_id].status = status
            return True
        return False

def test_bidirectional_task_sync():
    adapter = MockJiraAdapter()
    adapter.remote_db["PROJ-123"] = RemoteTask(
        remote_id="PROJ-123",
        title="Fix NullPointerException in billing",
        status="In Progress",
        description="Billing service throws NPE on empty cart"
    )

    # Fetch remote task
    task = adapter.fetch_task("PROJ-123")
    assert task is not None
    assert task.title == "Fix NullPointerException in billing"

    # Local review passed -> update remote status
    ok = adapter.update_task_status("PROJ-123", "Done")
    assert ok is True
    assert adapter.remote_db["PROJ-123"].status == "Done"

def test_confluence_knowledge_sync():
    from loopdesk.connectors.knowledge_source import KnowledgeSourceAdapter
    
    class MockConfluence(KnowledgeSourceAdapter):
        def fetch_doc(self, doc_id: str) -> str:
            if doc_id == "arch-doc-1":
                return "# Architecture Guidelines\nMicroservices use gRPC."
            return ""

    confluence = MockConfluence()
    content = confluence.fetch_doc("arch-doc-1")
    assert "Microservices use gRPC" in content
