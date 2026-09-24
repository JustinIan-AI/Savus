from __future__ import annotations

import os
import pty
import select
import signal
import subprocess
from typing import Dict, List, Optional

class PTYSession:
    """Represents an active, real OS PTY session managing an underlying subprocess."""
    def __init__(self, session_id: str, command: List[str], workdir: str) -> None:
        self.session_id = session_id
        self.command = command
        self.workdir = workdir
        self.is_detached = False
        
        # 打开真实伪终端 (Master / Slave)
        self.master_fd, self.slave_fd = pty.openpty()
        
        try:
            self._proc = subprocess.Popen(
                command,
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                cwd=workdir,
                close_fds=True,
                preexec_fn=os.setsid
            )
            self.pid = self._proc.pid
        finally:
            # 父进程必须关闭 slave_fd，防止保持打开阻塞 EOF
            os.close(self.slave_fd)
            self.slave_fd = -1

    def is_alive(self) -> bool:
        if not hasattr(self, '_proc') or self._proc is None:
            return False
        return self._proc.poll() is None

    def write(self, data: bytes) -> int:
        if not self.is_alive() or self.master_fd < 0:
            return 0
        return os.write(self.master_fd, data)

    def read(self, max_bytes: int = 4096, timeout: float = 0.5) -> bytes:
        if self.master_fd < 0:
            return b""
        r, _, _ = select.select([self.master_fd], [], [], timeout)
        if self.master_fd in r:
            try:
                return os.read(self.master_fd, max_bytes)
            except OSError:
                return b""
        return b""

    def terminate(self) -> None:
        if self.is_alive():
            try:
                os.killpg(os.getpgid(self.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                self._proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(self.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
        if self.master_fd >= 0:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = -1


class PTYSessionManager:
    """Manages creation, detachment, and lifecycle of real local agent PTY sessions."""
    def __init__(self) -> None:
        self._sessions: Dict[str, PTYSession] = {}

    def create_session(self, session_id: str, command: List[str], workdir: str) -> PTYSession:
        # 如果已存在同名会话且存活，先清理
        if session_id in self._sessions:
            self.terminate_session(session_id)
        session = PTYSession(session_id=session_id, command=command, workdir=workdir)
        self._sessions[session_id] = session
        return session

    def detach_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].is_detached = True

    def get_session(self, session_id: str) -> Optional[PTYSession]:
        return self._sessions.get(session_id)

    def terminate_session(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.terminate()
            del self._sessions[session_id]
