# 产品决策 — LoopDesk `loopdesk` 全量包名迁移

> 状态：已决策
> 版本：v1.0+
> 最后更新：2026-07-28
> 负责人：Product / Engineering
> 输入：`AGENTS.md`、`docs/decisions/module-audit-loopdesk-vs-opensquilla.md`、`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/plans/2026-07-28-loopdesk-v11-fdd-tdd-execution-plan.md`

## 1. 决策背景

OpenSquilla 的公共产品面已经统一为 `LoopDesk` / `loop_workspace` / `LOOP-STATE.json` / `loop` CLI；但内部 Python 包、部分 import 路径、发布资产和默认安装名仍沿用 `opensquilla`。这导致：

- 外部贡献者第一次看到源码时，容易把 LoopDesk 误解成 OpenSquilla 的换壳；
- 文档、CLI help、gateway 静态资源和 packaging 的命名边界长期不一致；
- 后续每个 release 都要重复解释“public surface 是 loopdesk，但 import 是 opensquilla”。

因此，需要在 v1.0+ 明确启动全量迁移，而不是继续把完整包名迁移留成开放式待办。

## 2. 决策结论

LoopDesk v1.0+ 已完成第一批 `opensquilla` → `loopdesk` 全量迁移。

当前已落地的迁移面：

- `pyproject.toml:88` 起提供 `loopdesk` / `loopdesk-gateway` 官方 script；
- `pyproject.toml:98` 的 package root 已切到 `src/loopdesk`；
- `src/loopdesk` 下已有完整可运行执行宿主、CLI、gateway、loop workspace 与 tests；
- `docs/decisions/loopdesk-v11-fdd-slices.md:1` 记录 v1.1 FDD slices。

后续 batch 可继续扩展 docs/workflows/scripts 的同步 rename。

### 2.1 全量迁移范围

| 层面 | 迁移动作 |
| --- | --- |
| Python 包名 | `src/opensquilla` 全量迁到 `src/loopdesk` |
| import 路径 | 全仓库 `from opensquilla.xxx` 改为 `from loopdesk.xxx` |
| CLI / gateway / docs / MCP | 公共命名统一为 `loopdesk` |
| 发布资产 | 安装名、模块名、package metadata 统一为 `loopdesk` |
| 用户可见状态 | 不再保留 `workspace-state.json`、`session` 等旧命名作为公共协议 |

### 2.2 迁移执行原则

- 以 **failing-test-first** 做迁移；每批 rename 必须带编译/import/test 门禁。
- 公共产品面先改，内部兼容层后清；不允许新的公共 surface 继续回退到 `opensquilla` 命名。
- 历史文档和内部 backlog 可保留 `OpenSquilla` 作为 runtime heritage 说明，但不得把它包装成当前产品名。

## 3. 边界说明

- 全量迁移指 **产品面 + Python 包面 + packaging 面** 全部对齐到 `loopdesk`；不是只改 CLI 帮助文本。
- 若某次迁移引入过高回归风险，应回滚该批次，而不是降低全量迁移目标。
- 已完成历史发布版本可保留旧包名引用，但当前 main/v1.0+ 的官方 source 必须已经迁移。
- 与 `docs/decisions/module-audit-loopdesk-vs-opensquilla.md` 的关系：该审计继续生效；cancel modules 不得借全量迁移重新回到公共产品面。

## 4. 验证方式

- 全量 import grep / packaging metadata 回归；
- `pytest -q` 覆盖被 rename 的 runtime、CLI、gateway、loop workspace 路径；
- release/acceptance 文档必须显式说明当前官方包名是 `loopdesk`。
