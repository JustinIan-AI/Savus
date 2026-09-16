# LoopDesk 设计系统

> 版本：**v2.0**
> 日期：2026-09-14
> 范围：LoopDesk **v2.0 团队循环工作区** 的本地 Web UI（Codex 三栏范式：任务看板 / 团队资产市场 / 设置）
> 定位依据：`docs/product-positioning.md`（v2.0 团队版）
> 结构与行为：`docs/plans/loopdesk-webui-design-spec.md`（v2.0）
> 视觉参考实现：Ardot 设计文件 `724693301521075`（8 帧）
> 实现稿：`frontend/`（React 18 + TypeScript + Vite 6 + Tailwind v4）；token 落地于 `frontend/src/index.css`
> 取代：**v0.1-draft**（2026-07-15，个人版 / 浅色默认 / teal `#0E8F86`）——已作废，见 §10

这是 LoopDesk Web UI 的**视觉唯一事实源**。前端 MUST 以 CSS 自定义属性（或等价 token 导出）消费这里的值，不得在本文件之外硬编码原始颜色、尺寸或间距。

> **Token 值取自实现稿实测**，与 Ardot 画布 1:1 采样值一致。若文档与代码冲突，以本文件为准并修正代码（而非反向）。

---

## 1. 设计语言

**一句话：** 面向研发团队的冷静、技术、高密度控制台——**连续性优先于炫技**。

**原则：**

- **local-first、低噪音**。没有营销光泽，没有"hero"区块，没有装饰性渐变。
- **信息密度是特性，不是缺陷**——但必须保持清晰可读。
- **一个主强调色**（emerald）承担主操作与活动态；其余色相只用于**语义**（信息 / 警告 / 资产分类），不做装饰。
- **系统驱动的节奏**：每个屏幕使用同一套间距刻度、圆角与字体层级。
- **深色为唯一交付主题**（见 §2）。
- **可见护栏**：审批、预算、diff、验证徽标、运行日志必须看得见、控得住——专业性靠护栏而非术语。

**禁止的模式（不要发布）：**

- chrome 或结构性表面上的彩虹 / 多色渐变。
- 主面板上的重度毛玻璃效果。
- 把 emoji 当功能图标。
- 同一组件族内圆角不一致。
- 装饰性光斑、环境光晕，或仅有插画的状态。
- 纯颜色状态（始终把色相与标签或图标 + 文本配对）。

---

## 2. 颜色 Token

### 2.1 v2.0 交付主题：深色（Dark）

v2.0 **只交付深色主题**：Ardot 画布 8 帧与实现稿 `frontend/src/index.css` 均为深色。

> v0.1-draft 曾定义浅色主题（`#FFFFFF` 基底）。该主题**未纳入 v2.0**，其色值已作废。如后续需要浅色，必须基于本节深色 token **重新推导**，不得沿用 v0.1 浅色值。

#### 表面（Surfaces）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--c-base` | `#0B0E14` | 画布 / 应用背景 |
| `--c-rail` | `#0E1118` | 左栏、右侧上下文面板、内嵌井 |
| `--c-surface` | `#151922` | 抬升表面：卡片、输入框、抽屉、模态 |
| `--c-selected` | `#13261D` | 活动 / 选中行底色（emerald 暗调） |
| `--c-pill` | `#182437` | 分支 pill、信息类 chip 底色 |

#### 线条（Lines）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--c-border` | `#1B2030` | 面板与表格细线 |
| `--c-border-head` | `#1C212B` | TopBar / 表头分隔线 |
| `--c-divider` | `#212630` | 内嵌盒与卡片描边 |
| `--c-chip` | `#242936` | chip、输入框、kbd |
| `--c-proj-active` | `#29303D` | 活动项目外框 |
| `--c-kbd` | `#333B4A` | 键盘按键描边 |
| `--c-avatar` | `#2A313D` | 头像底 |

#### 强调与语义（Accents & Semantics）

| Token | 值 | 角色 | 用法 |
| --- | --- | --- | --- |
| `--c-emerald` | `#34D399` | **主强调** | 主操作（新建会话 / 确认添加）、活动态、开关开启、Skill 类资产 |
| `--c-emerald-edge` | `#33D499` | 主强调描边 | emerald 元素的边框细描 |
| `--c-blue` | `#5B9DFF` | 信息 / 中性强调 | 分支 pill、Rule 类资产、进行中说明 |
| `--c-amber` | `#E8A33D` | 警告 / 受限 | 只读提示、无权限、接近上限、已升级 |
| `--c-teal` | `#2DD4BF` | 次强调 | MCP 类资产、次级高亮 |

**语义色井（tinted wells）**——用于资产卡片与警示区的低饱和底色：

| Token | 值 | 用途 |
| --- | --- | --- |
| `--c-warn-well` | `#1A1611` | 只读 / 受限警示区底 |
| `--c-cmd-well` | `#0F172A` | Command 类资产底 |
| `--c-mcp-well` | `#0B1F1E` | MCP 类资产底 |

#### 文本（Type color）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--c-tp` | `#E6E9EF` | 主文本：正文、标题、激活项 |
| `--c-ts` | `#9AA3B2` | 次文本：标签、meta、表头 |
| `--c-tm` | `#6B727F` | 弱文本：提示、时间戳、禁用 |

> **状态再映射**：任务状态（待办 / 进行中 / 评审中 / 已完成）与审批态统一走 `--c-tm` / `--c-blue` / `--c-amber` / `--c-emerald`，**必须带文本标签**渲染，不得只靠颜色。

---

## 3. 字体与排版

### 3.1 字体栈

```css
--f-sans:    'Noto Sans SC', 'Sarasa Gothic SC', 'PingFang SC', 'Hiragino Sans GB',
             'Microsoft YaHei', system-ui, sans-serif;
--f-display: 'Geist', 'Noto Sans SC', system-ui, sans-serif;
--f-mono:    'Geist Mono', ui-monospace, 'SFMono-Regular', 'JetBrains Mono', Menlo, monospace;
```

- `--f-sans`：中文 UI 正文与标签的默认族。
- `--f-display`：品牌字标、版本号、头像缩写等需要几何感的少数位置。
- `--f-mono`：**高频使用**——工作区根路径、`LOOP-STATE.json` 键、token / 成本数字、会话 key、代码与工具调用输出、表头序号。

### 3.2 字号刻度（实测于实现稿，按频次归纳）

| Token | 字号 | 用途 |
| --- | --- | --- |
| `--t-xs` | 10px | 极小标注、图标旁角标 |
| `--t-sm` | 11px | meta、时间戳、pill 文本、表头 |
| `--t-md` | 12px | 次要正文、卡片副标题、设置项说明 |
| `--t-base` | **13px** | **基准正文**：卡片标题、导航项、列表行 |
| `--t-lg` | 14px | 区块标题、TopBar 文本、面板标题 |
| `--t-xl` | 16px | 页面 / 面板主标题 |
| `--t-2xl` | 24px | 品牌字标 |

- 字重：正文 `400`；标签 / 控件 / 表头 `500`；标题 `600`。**避免 `700` 及以上**。
- 数字数据（花费、计数、时长、并发数）使用 `font-variant-numeric: tabular-nums`，并优先配 `--f-mono`。

### 3.3 行高 —— **必须写死像素**（硬规则）

画布 TEXT 节点使用**固定像素行高**；浏览器 `line-height: normal`（≈1.5×）会导致纵向逐级漂移，多屏对齐全部失效。

- **每个文字元素都要显式给出 `lineHeight: 'NNpx'`**。
- **不要设置全局 line-height**——会破坏其他屏已校准的节奏。
- 实测在用的行高值（与字号配对）：

| 字号 | 行高 |
| --- | --- |
| 11px | 14px |
| 12px | 15–16px |
| 13px | 18px |
| 14px | 20px |
| 16px | 24px |
| 24px | 30px |

---

## 4. 间距、布局与密度

### 4.1 间距刻度

**基准单位 4px。** 不要使用任意 margin，从刻度组合。

| Token | px | | Token | px |
| --- | --- | --- | --- | --- |
| `--space-1` | 4 | | `--space-6` | 24 |
| `--space-2` | 8 | | `--space-8` | 32 |
| `--space-3` | 12 | | `--space-10` | 40 |
| `--space-4` | 16 | | `--space-12` | 48 |
| `--space-5` | 20 | | | |

实测高频值：`12`（卡片内边距）→ `20` → `8` / `6`（行内 gap）→ `24`（区块间距）。

### 4.2 三栏布局（Codex 范式）

画布 **1440×900 原始像素**，实现保持 **1:1 不缩放**。

| 区域 | 宽度 | 说明 |
| --- | --- | --- |
| 左栏 Left Rail | **240px** | 品牌 + 新建会话 + 导航（任务看板 / 团队资产 / 设置）+ 项目分组 |
| 中栏 Center | `fill` | TopBar（项目切换 / 搜索 / 状态 pill / 头像）+ 看板或详情 + 底部会话框 |
| 右栏 Right Panel | **360px** | 上下文面板：任务概览 / 进度 / 成本 / 审批 / 变更 diff / Agent 会话 / 证据 / Handoff |

- 三栏**恒定**：专业能力通过右栏 / 设置渐进披露，**不新增顶层页面**。
- 响应式：Desktop 三栏 → Tablet 收起右栏 → Mobile 单列（左栏转底部标签栏）。
- 浮层：会话列表抽屉自左侧 320px 滑出；添加 Agent / 添加连接器为居中模态 + scrim。

### 4.3 密度

默认且唯一模式是 **Compact**（开发者工具，高信息密度）。

| Token | 值 |
| --- | --- |
| `--control-h-sm` | 28px |
| `--control-h-md` | 32px |
| `--control-h-lg` | 36px |
| `--row-h` | 36px |
| `--input-h` | 32px |

不要在同一屏幕内混用密度模式。若未来需要"宽松"使用面（onboarding、空态），请切换**整个使用面**，而非单个区域。

---

## 5. 圆角、边框、阴影

```css
--radius-sm:   6px;
--radius-md:   8px;    /* 默认：卡片、输入框、按钮 */
--radius-lg:   12px;   /* 模态、浮层 */
--radius-full: 9999px; /* 药丸、状态 chip、头像 */

--border-width: 1px;

--shadow-drawer: 8px 0 24px rgba(0, 0, 0, 0.45);  /* 侧滑抽屉 */
--shadow-modal:  0 12px 28px rgba(0, 0, 0, 0.50); /* 居中模态 */
```

- 卡片与输入框：`--radius-md` + `--c-border`，**默认无阴影**；仅在悬停 / 浮层时抬升。
- 状态 chip 与徽标：`--radius-full`。
- 模态 / 抽屉：`--radius-lg`（抽屉为直角贴合视口）+ 对应阴影。
- 实测圆角分布：`8px`（主）> `10px` > `6px` > `12px` > `4px`。**不要混用未在刻度内的值。**

---

## 6. 组件（token 驱动）

### 6.1 按钮

| 变体 | token 用法 | 用途 |
| --- | --- | --- |
| Primary | `bg: --c-emerald`、`text: --c-base`、`radius-md` | 每个屏幕 / 区块一个（新建会话、确认添加） |
| Secondary | `bg: --c-chip`、`text: --c-tp`、`border: --c-border` | 辅助动作（取消） |
| Ghost | `bg: transparent`、`text: --c-ts` | 低强调 / 内联 |
| Danger | `bg: --c-amber` 或红色系、`text` 对比色 | 破坏性操作——**先确认** |
| Disabled | `bg: --c-chip`、`text: --c-tm` | 无权限（如"下发到团队（无权限）"） |

高度 `--control-h-md`；水平内边距 `--space-4`。**每个区域一个主操作。**

### 6.2 状态 chip / 徽标

药丸形（`--radius-full`），`--t-sm`，字重 `500`，`bg: <语义>-well`，`text: <语义色>`。**务必包含文本标签**（如 `claude·3 运行`、`codex·空闲`），不可只靠颜色。

### 6.3 卡片 / 面板

`bg: --c-surface`、`border: --c-border`、`radius-md`，内边距 `--space-3`（紧凑）/`--space-4`。资产卡片按类型使用 `--c-*-well` 底。仅在需要下沉某区域时用 `--c-rail`，绝不用于装饰。

### 6.4 输入框

`bg: --c-chip` 或 `--c-surface`、`border: --c-border`、`radius-md`、`--input-h`、`--t-base`。焦点：`border: --c-emerald`。路径 / key / token 使用 `--f-mono`。

### 6.5 表格

行高 `--row-h`，单元内边距 `0 --space-4`，表头 `bg: --c-rail`、`--t-sm`、`--c-ts`。仅当行数 > 20 时使用斑马纹。状态列使用 §6.2 chip —— 设置页的 Agent 表、MCP 连接器表均按此规范。

### 6.6 导航项

左栏导航与设置子导航：`--t-base`；非活动 `text: --c-ts`；**活动项** `text: --c-emerald` + 左侧 emerald 活动条 + `bg: --c-selected`。

### 6.7 Tabs

下划线样式：活动 tab `text: --c-tp` + `border-bottom: 2px --c-emerald`；非活动 `text: --c-ts`。控制台 chrome 中**不使用填充式药丸 tabs**。

### 6.8 开关

药丸形；开启 `bg: --c-emerald`，关闭 `bg: --c-chip`。设置页的成本闸门 / 安全闸门 / Worktree 隔离均使用此控件。

---

## 7. 图标

- 描边式，`1.5px`，`currentColor`，尺寸 **16px**（内联）/ **20px**（区块）。
- 只使用一套图标集。不要用 emoji 当功能图标。
- 图标不得替代导航或主操作中的必要文本标签。

---

## 8. 动效

- 时长 `<= 200ms`，缓动 `cubic-bezier(0.2, 0, 0, 1)`。
- 尊重 `prefers-reduced-motion: reduce`——禁用非必要过渡。
- 数据使用面不做入场动画；仅在状态变化（悬停、打开）时过渡。

---

## 9. 无障碍基线

- 文本对比度：`--c-tp` vs `--c-base` ≥ `4.5:1`；大字 ≥ `3:1`。
- 每个交互元素都有可见焦点环（见 §6.4）。
- 全键盘可操作；`Esc` 关闭浮层；`Enter` 提交主操作。
- 状态以**文本 + 颜色**表达，绝不仅靠颜色（WCAG 1.4.1）。

---

## 10. v0.1 → v2.0 迁移对照（防偏差）

v0.1-draft 的以下取值与命名**已作废**，实现时一律以本文件 §2–§6 为准：

| 维度 | v0.1-draft（作废） | **v2.0（现行）** |
| --- | --- | --- |
| 交付主题 | 浅色默认 + 深色 | **仅深色** |
| 主强调色 | teal `#0E8F86`（浅）/ `#15B8A6`（深） | **emerald `#34D399`** |
| 应用背景 | `#FFFFFF` / `#0E1116` | `#0B0E14` |
| 抬升表面 | —（未定义） | `#151922` |
| 边框 | `#E2E6EC` / `#262E38` | `#1B2030` / `#1C212B` |
| 主文本 | `#1A1F29` / `#E6EAF0` | `#E6E9EF` |
| 警告 | `#C2841A` | `#E8A33D` |
| 信息 | `#2D7FF0` | `#5B9DFF` |
| 字体栈 | `-apple-system` 系统栈 | **`Geist` / `Geist Mono` / `Noto Sans SC` + `Sarasa Gothic SC`** |
| 基准字号 | 14px | **13px** |
| 布局 | 居中内容列 `1200px` + 双栏 `1.4fr / 1fr` | **三栏：240 左栏 + `fill` 中栏 + 360 右栏，画布 1440×900 1:1** |
| 阴影 | `0 1px 2px / 0 4px 12px / 0 12px 32px`（浅色系） | `--shadow-drawer` / `--shadow-modal`（黑色系） |
| Token 命名 | `--bg-base` / `--accent` / `--text-primary` | `--c-base` / `--c-emerald` / `--c-tp` |

**保留未变**：4px 间距基准、圆角刻度（6/8/12/full）、图标规范、动效规范、无障碍基线、状态必须"颜色 + 文本"的表达原则。

> 命名备注：v0.1 的语义化命名（`--bg-base` 等）在 v2.0 被实现稿的紧凑命名（`--c-*` / `--f-*` / `--t-*`）取代，以便与 `frontend/src/index.css` 1:1 对齐。**不要在代码中同时存在两套命名。**
