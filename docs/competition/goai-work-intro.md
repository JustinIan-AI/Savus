# LoopDesk · 参赛作品简介（约 500 字 · 对应 PPT P0）

**作品名称**：LoopDesk —— 可验证交付的 Agent 研发运行时

**一句话定位**：把 LoopDesk 作为 AgentTeams 的第四种 Worker Runtime，让 AI 研发交付从"自己说完成"变成"被独立验证过"。

**核心问题**：企业引入 AI 编码 Agent 后，真正的瓶颈不是 Agent 不会写代码，而是 Agent 说它写完了却没人能证明。AgentTeams 官方也承认其 Worker 的"完成"只是房间里的自然语言断言，没有任何机制验证"done"是否真实；多 Agent 并行改同一代码库时，还缺工作区隔离、独立验证、证据留痕与回滚能力。

**解决方案**：以 AgentTeams 为协同治理平面（声明式 CRD、Matrix 审计、Higress 凭证隔离、MinIO 共享存储），LoopDesk 作为可插拔的 `spec.runtime: loopdesk` Worker 承担长程执行，并补齐官方声明不做的运行时可靠性层——引入权限强制隔离的独立 Verifier Agent，其判定只依据真实测试/构建的退出码与产物哈希，产出机器可读的 Validation Receipt；配套全链路证据沉淀（Trace + Receipt + Evidence Bundle）、人工审批门禁（Human CRD）与 worktree 级回滚。四个职能 Agent（Planner / Executor / Verifier / Curator）加一个人类审批者，覆盖赛道八步闭环，第 5 步 Receipt 是唯一的"通过"凭证，FAIL 则回环重规划。

**创新与差异化**：① 独立验证靠"上下文隔离 / 权限隔离 / 证据锚定"三重工程强制，不靠 prompt 约定；② 不重造编排框架，而是作为现有生态的第四种 runtime 接入；③ 提出可复现评测方法（LoopDesk 自举回归集，以自身真实 bug commit 为 ground truth）与招牌指标 False-Done Rate（误报完成率）。

**复用与开放**：Worker 适配层、Receipt JSON Schema、7 个新 Skill、自举回归集全部 Apache-2.0 开放；Receipt Schema 与 Skill 可被任意 AgentTeams 团队直接复用。LoopDesk 已发布 v0.3.1（Apache-2.0，625 测试文件可离线运行），MCP 双向、62 个 Skill、向量记忆、Trace 回放、权限矩阵、human gate、git worktree 隔离、预算控制均已实现，构成本方案的实证基础。
