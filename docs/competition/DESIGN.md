# GOAI Agent Infra 初赛 PPT · 视觉设计文档

> 配色严格参照用户提供的初赛官方 PPT 模板（2e567d1a...pptx）实测提取，不另起炉灶。

## 1. 画布与母版（三区 A/B/C）
- 画布 1280×720，padding 上 20 / 下 20 / 左右 64
- A 标题块 0–112px：主标题 32px bold（navy），左侧 6px 橙色竖条装饰
- B 内容区 112–660px：正文/图表/卡片
- C 页脚条 660–720px：左侧 "LoopDesk · GOAI 新智基座 Agent Infra 赛道" 14px #9AA1B8，右侧页码 `NN / 19` 14px #9AA1B8
- 封面 / 章节过渡 / 结束页用自定义版式（深色满铺）

## 2. 颜色系统（来自官方模板，实测 hex）
| 角色 | hex | 用途 |
| :--- | :--- | :--- |
| 主色·藏蓝 | `#1B1F3B` | 深色块、标题、白底上的正文 |
| 强调色·品牌橙 | `#FF6B35` | 关键数字、焦点条、章节号、CTA、评级徽标 |
| 辅色·中蓝 | `#2A2F5B` | 卡片头、次级色块、分隔 |
| 中性灰 | `#6B7280` | 次级正文 |
| 浅灰 | `#9AA1B8` | 页脚、弱化文字 |
| 浅橙底 | `#FFEDE4` | 卡片浅底 |
| 浅蓝底 | `#E9EEFB` | 卡片浅底 |
| 背景 | `#FFFFFF` | 内容页底色 |

面积分配：内容页 主色(navy文字/深色块)≤60% / 辅色(中蓝卡头)≤30% / 强调橙≤10%（仅焦点）；hero/过渡页 橙可升至 15–20%。

## 3. 字体系统
- 中文标题/正文：`Source Han Sans SC`（苹方回退 `PingFang SC`）
- 西文/数字：`Inter`（`Helvetica Neue` 回退）
- 字号阶梯：封面主标 64 / 章节大字 60 / 巨型锚点 72–96 / 页标题 32 / 卡头 22 / 正文 18–20 / 脚注 14
- 全局仅 2 套字体家族（中文黑体 + 西文无衬线），数码/数字用 Inter 拉开表现力。

## 4. 视觉锚点规则
- 每页 ≥1 个视觉锚点（≥44px 元素 或 ≥40% B 区图）；封面/过渡用大章节号或大字。
- 配图以 SVG 为主（架构图 / 八步闭环 / Agent 拓扑 / Skill 三层 / 里程碑），干净矢量、统一橙+navy。
- 禁止装饰小贴片塞标题栏；禁止全篇同色比例雷同。

## 5. 页面映射表
| # | 文件 | 类型 | 角色 | 版式 | 主色分配 | 关键约束 |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | 01_cover | cover | hero | 深色满铺+大标题+橙条 | 橙20% | 主标64 |
| 02 | 02_p0 | onepager | supporting | 六宫格关键事实 | 橙10% | 每格≥80字 |
| 03 | 03_toc | catalog | supporting | 八章纵向列表 | 橙8% | 每章≥20字 |
| 04 | 04_ch1 | divider | transition | 大章节号01+标题 | 橙18% | 过渡页 |
| 05 | 05_ch1 | content | supporting | 痛点5卡+洞察 | 橙10% | 5卡等高 |
| 06 | 06_ch2 | divider | transition | 大章节号02 | 橙18% | 过渡页 |
| 07 | 07_ch2 | content | supporting | 分层架构SVG | 橙12% | SVG≥B40% |
| 08 | 08_ch3 | divider | transition | 大章节号03 | 橙18% | 过渡页 |
| 09 | 09_ch3 | content | supporting | 4 Agent+Verifier拓扑 | 橙12% | SVG |
| 10 | 10_ch4 | divider | transition | 大章节号04 | 橙18% | 过渡页 |
| 11 | 11_ch4 | content | supporting | Skill三层+7新 | 橙10% | 三层卡 |
| 12 | 12_ch5 | divider | transition | 大章节号05 | 橙18% | 过渡页 |
| 13 | 13_ch5 | content | supporting | 可观测/安全/验证三栏 | 橙10% | 三栏 |
| 14 | 14_ch6 | divider | transition | 大章节号06 | 橙18% | 过渡页 |
| 15 | 15_ch6 | content | supporting | 开源/迁移列表 | 橙8% | 文本页放大 |
| 16 | 16_ch7 | divider | transition | 大章节号07 | 橙18% | 过渡页 |
| 17 | 17_ch7 | content | supporting | 里程碑+风险 | 橙10% | 里程碑轴 |
| 18 | 18_ch8 | divider | transition | 大章节号08 | 橙18% | 过渡页 |
| 19 | 19_ch8 | content | supporting | 团队占位 | 橙8% | 占位待填 |
