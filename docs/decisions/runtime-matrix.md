# 产品决策 — LoopDesk v1.1 Runtime Matrix 与 Desktop Packaging Boundary

> 状态：已决策
> 版本：v1.1
> 最后更新：2026-07-28
> 负责人：Product / Engineering
> 输入：`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/decisions/desktop-web-im-product-boundary.md`、`docs/decisions/product-strategy.md`、`docs/decisions/prd-v1.1-review-checklist.md`

## 1. 决策背景

v1.1 的对外叙事需要同时回答两个边界问题：

- 哪些 coding agent runtime 属于 LoopDesk 当前官方支持矩阵；
- Desktop 是重 GUI shell，还是本地 runtime + system launcher。

## 2. 决策结论

### 2.1 Runtime Matrix

LoopDesk v1.1 采用 **MCP-first、tool-specific adapter + local CLI** 的官方支持策略；当前官方支持 runtime：

| runtime_id | 展示名 | transport | primary_interface | notes |
| --- | --- | --- | --- | --- |
| `claude-code` | Claude Code | native_cli | terminal | Primary local coding runtime |
| `codex-cli` | Codex CLI | native_cli | terminal | Primary local coding runtime |
| `codebuddy` | Codebuddy | native_cli | terminal | Supported local coding runtime |
| `trae` | Trae | native_cli | terminal | Supported local coding runtime |
| `opencode` | OpenCode | native_cli | terminal | Official v1.1 supported runtime |
| `gemini` | Gemini / Local CLIs | native_cli | terminal | Supported local coding runtime |

实现锚点：`src/loopdesk/loop_workspace/runtime_matrix.py`

### 2.2 Desktop Packaging Boundary

LoopDesk v1.1 锁定 **local runtime + system launcher**，不做 Electron shell。

- Desktop 负责启动本地 gateway、repair local runtime、打开 inspection shortcut；
- 所有 durable state 继续归属本地 workspace；
- Web/IM 不得替代本地 gateway authority；
- 明确排除：`electron_shell`、`cloud_sync`、`team_room`、`saas_runtime`。

## 3. 边界说明

- 官方支持不等于每个 runtime 都具备同等深度 adapter；v1.1 先统一能力矩阵，再按实际 handoff 证据补齐 transport 细节。
- Desktop launcher 不是新的执行平面；执行平面仍是本地 gateway + local coding runtime + worktree isolation。
- 如需新增 runtime，应先进入 `docs/decisions/runtime-matrix.md` 和 `docs/plans/prd-v1.2-gap-backlog.md` 评审，而不是直接修改官方支持矩阵。

## 1.1 v1.2 补充决策

v1.2 不新增官方 runtime，但把 runtime matrix 从展示名单升级为 **可校验 contract**：

- `RuntimeCapabilityProfile` 显式声明 `capability_profile_keys` 与最小 schema；
- 默认能力锚点为 Claude Code、Codex CLI、Gemini；
- 能力契约用于 planner/router 决策，不扩展 team-room、cloud-sync、IM-first 边界。

### 2.2 OpenCode 支持边界

OpenCode 保留在 v1.1 官方支持矩阵，但 v1.2 不新增官方深度适配：

- 继续以 `native_cli` + `terminal` 的通用 local CLI 身份存在；
- 不做 v1.2 专属 adapter、transport 细节补齐或 router 优先绑定；
- 若后续要提升支持深度，先回到 `docs/plans/prd-v1.2-gap-backlog.md` 评审，再扩展矩阵。

## 4. 验证方式

- `tests/test_loop_workspace/test_runtime_matrix.py` 覆盖官方支持矩阵与桌面边界；
- `docs/prd/personal-loop-workspace-v1.1.zh.md` 必须在 runtime 相关叙事中引用本决策。
