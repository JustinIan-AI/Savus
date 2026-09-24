from __future__ import annotations

import os
import time
import pytest
from loopdesk.orchestration.pty_manager import PTYSessionManager

def test_pty_real_process_execution_and_io():
    manager = PTYSessionManager()
    
    # 启动一个真实运行的交互式 shell 命令 (cat 等待输入)
    session = manager.create_session(
        session_id="real-sess-1",
        command=["cat"],
        workdir="/tmp"
    )
    
    assert session.session_id == "real-sess-1"
    assert session.pid > 0
    assert session.is_alive() is True
    
    # 向真实 PTY 写入数据
    session.write(b"hello pty\n")
    time.sleep(0.1)
    
    # 从真实 PTY 读取回显输出
    output = session.read(1024)
    assert b"hello pty" in output
    
    # 分离会话 (Detach) 检查状态保持存活
    manager.detach_session("real-sess-1")
    reattached = manager.get_session("real-sess-1")
    assert reattached is not None
    assert reattached.is_detached is True
    assert reattached.is_alive() is True
    
    # 终止会话 (Terminate)
    manager.terminate_session("real-sess-1")
    time.sleep(0.1)
    assert reattached.is_alive() is False
