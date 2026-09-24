#!/usr/bin/env python3
"""LoopDesk WebUI × gateway —— 任务全生命周期前后端接线复验（真实浏览器 + 真实 HTTP）。

断言口径：不是「页面点得动」，而是「前端确实调用了后端，且后端状态反过来改变了界面」。

覆盖的生命周期动作（全部只走界面）：
  新建任务 → 提交评审（PATCH）→ 状态下拉（PATCH 到 阻塞）→ 审批门通过 / 打回
  → 详情页复制宿主命令 → SSE 外部注入自动上板

运行：  .venv/bin/python tests/verify_webui_lifecycle.py
前置：  loopdesk gateway run --port 18792（并已完成 `npm run build`）

脚本会改工作区的 LOOP-STATE.json（这正是被测对象），且开头会把三张画布卡
复位到「进行中」—— 这是**测试前置**，让走查从一个确定的状态出发，否则上一次
走查留下的状态会让下一次找不到「提交评审」按钮。跑前先备份：
  cp LOOP-STATE.json /tmp/loopdesk-lifecycle/LOOP-STATE.bak.json
"""

from __future__ import annotations

import asyncio
import json
import urllib.request

from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:18792"
API = "/api/v1"
PROJECT = "default"

NEW_TASK_DESC = "接通网关后由前端落库的验证任务"
# 画布「进行中」列的三张卡（帧 01），每张承担一个生命周期动作
SUBMIT_CARD, SUBMIT_CARD_TITLE = "ACME-201", "实现跨会话 handoff 上下文传递"
MENU_CARD, MENU_CARD_TITLE = "ACME-209", "并行运行 issue-fix 模板修复内存泄漏"
GATE_CARD, GATE_CARD_TITLE = "ACME-196", "为网关补充限流与熔断策略"
# 「状态 ▾」的取值一律用后端 LoopWorkspaceStatus 原名
STATUS_OPTIONS = ["planned", "active", "in_review", "blocked", "completed", "canceled"]

RESULTS: list[tuple[str, bool, str]] = []


def log(step: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((step, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {step}" + (f"   [{detail}]" if detail else ""))


def http(method: str, path: str, payload: dict | None = None):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def task_record(task_id: str) -> dict:
    _, body = http("GET", f"{API}/projects/{PROJECT}/tasks")
    if not isinstance(body, dict):
        return {}
    return next((t for t in (body.get("tasks") or []) if t.get("id") == task_id), {})


async def main() -> int:
    # ---------------- 阶段 0b · 测试前置：复位画布卡 ----------------
    for cid, title in (
        (SUBMIT_CARD, SUBMIT_CARD_TITLE),
        (MENU_CARD, MENU_CARD_TITLE),
        (GATE_CARD, GATE_CARD_TITLE),
    ):
        code, _ = http("PATCH", f"{API}/tasks/{cid}", {"status": "active", "title": title})
        if code != 200:
            print(f"前置复位失败：{cid} -> {code}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            # 「复制」写的是真实剪贴板，没有权限就只能测到「按钮点了不报错」
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = await ctx.new_page()

        api_calls: list[tuple[str, str]] = []
        api_bodies: list[dict] = []
        console_errors: list[str] = []

        def on_request(r):
            if "/api/" in r.url:
                api_calls.append((r.method, r.url))
                if r.post_data:
                    try:
                        api_bodies.append(json.loads(r.post_data))
                    except Exception:  # noqa: BLE001
                        pass

        page.on("request", on_request)
        page.on(
            "console",
            lambda m: console_errors.append(f"console:{m.text}") if m.type == "error" else None,
        )
        page.on("pageerror", lambda e: console_errors.append(f"pageerror:{e}"))

        def api_hits(method: str, needle: str) -> list[str]:
            return [u for m, u in api_calls if m == method and needle in u]

        async def wait_api(method: str, needle: str, timeout: int = 6000) -> bool:
            waited = 0
            while waited < timeout:
                if api_hits(method, needle):
                    return True
                await page.wait_for_timeout(200)
                waited += 200
            return False

        async def card_ids(column: str) -> list[str]:
            return await page.locator(
                f"[data-column='{column}'] [data-card-id]"
            ).evaluate_all("els => els.map(e => e.dataset.cardId)")

        async def wait_card(column: str, card_id: str, timeout: int = 8000) -> bool:
            waited = 0
            while waited < timeout:
                if card_id in await card_ids(column):
                    return True
                await page.wait_for_timeout(200)
                waited += 200
            return False

        async def badge(column: str) -> int:
            """列头徽标数字。只按**增量**断言 —— 基数取决于工作区里已有多少任务。"""
            txt = await page.locator(f"[data-column='{column}']").first.locator("span").nth(1).inner_text()
            return int(txt.strip())

        # ---------------- 阶段 0 · 载入与接线存活 ----------------
        await page.goto(BASE + "/", wait_until="load")
        await page.wait_for_timeout(2500)

        root = page.locator("[data-loopdesk-tasks]")
        online = await root.get_attribute("data-loopdesk-online")
        n_tasks = int(await root.get_attribute("data-loopdesk-tasks") or 0)

        hits = api_hits("GET", f"{API}/projects/{PROJECT}/tasks")
        log("01 载入即拉任务快照 GET /api/v1/projects/{id}/tasks", bool(hits), f"命中 {len(hits)} 次")
        log(
            "02 事件总线 SSE GET /api/v1/events 已连接",
            bool(api_hits("GET", f"{API}/events")),
            f"命中 {len(api_hits('GET', f'{API}/events'))} 次",
        )
        log("03 接线状态 data-loopdesk-online = true", online == "true", f"值={online}")
        log("04 后端任务数已进前端 data-loopdesk-tasks", n_tasks >= 1, f"值={n_tasks}")

        # ---------------- 阶段 1 · 看板 = 画布种子 ⊕ 后端任务 ----------------
        seeded = {
            cid: await page.locator(f"[data-card-id='{cid}']").count()
            for cid in ("ACME-218", "ACME-201", "ACME-196", "ACME-172")
        }
        log("05 画布种子卡片仍在（设计稿 8 张卡不被后端顶掉）", all(v == 1 for v in seeded.values()), str(seeded))

        log("06 看板仍是四列", await page.locator("[data-column]").count() == 4, "列数=4")

        doing = await card_ids("doing")
        log(
            "07 后端独有的任务已作为真卡片叠进看板",
            any(cid.startswith("task-") for cid in doing),
            f"进行中={doing}",
        )

        # ---------------- 阶段 2 · 新建任务落库 ----------------
        await page.locator("button:has-text('新建任务')").first.click()
        await page.wait_for_timeout(500)
        modal_seen = await page.locator("[data-testid='new-task-desc']").count() == 1
        await page.locator("[data-testid='new-task-desc']").fill(NEW_TASK_DESC)
        await page.locator("button:has-text('开始任务')").click()

        created = await wait_api("POST", f"{API}/projects/{PROJECT}/tasks")
        await page.wait_for_timeout(1200)
        board_text = await page.locator("main").inner_text()
        log("08 新建任务面板可见且描述可输入", modal_seen, "描述是真实 textarea")
        log("09 「开始任务」→ POST /api/v1/projects/{id}/tasks", created, "请求已发出")
        log("10 新任务出现在看板上", NEW_TASK_DESC in board_text, f"标题={NEW_TASK_DESC}")

        _, body = http("GET", f"{API}/projects/{PROJECT}/tasks")
        titles = [t.get("title") for t in (body.get("tasks") or [])] if isinstance(body, dict) else []
        log("11 HTTP 交叉核对：任务真的落库了", NEW_TASK_DESC in titles, f"后端标题数={len(titles)}")

        # ---------------- 阶段 3 · 提交评审（进行中 → 评审中，走 PATCH） ----------------
        actions = await page.locator(
            f"[data-card-id='{SUBMIT_CARD}'] button"
        ).evaluate_all("els => els.map(e => e.dataset.action)")
        log(
            "12 进行中卡片带「提交评审 / 状态 ▾」两枚动作",
            actions == ["submit-review", "set-status"],
            f"动作={actions}",
        )

        b_before = {c: await badge(c) for c in ("doing", "review")}
        await page.locator(f"[data-card-id='{SUBMIT_CARD}'] [data-action='submit-review']").click()
        patched = await wait_api("PATCH", f"{API}/tasks/{SUBMIT_CARD}")
        moved = await wait_card("review", SUBMIT_CARD)
        log("13 「提交评审」→ PATCH /api/v1/tasks/{id}", patched, "请求已发出")
        log("14 卡片随后端状态换列（进行中 → 评审中）", moved, f"评审中列={await card_ids('review')}")

        b_after = {c: await badge(c) for c in ("doing", "review")}
        log(
            "15 列头徽标同步（进行中 −1、评审中 +1）",
            b_after["doing"] == b_before["doing"] - 1 and b_after["review"] == b_before["review"] + 1,
            f"进行中 {b_before['doing']}→{b_after['doing']}，评审中 {b_before['review']}→{b_after['review']}",
        )

        rec = task_record(SUBMIT_CARD)
        log(
            "16 HTTP 交叉核对：后端 status=in_review，且标题未被改写",
            rec.get("status") == "in_review" and rec.get("title") == SUBMIT_CARD_TITLE,
            f"status={rec.get('status')} title={rec.get('title')!r}",
        )

        # ---------------- 阶段 4 · 状态 ▾ 下拉（进行中 → 阻塞 · 需返工） ----------------
        await page.locator(f"[data-card-id='{MENU_CARD}'] [data-action='set-status']").click()
        await page.wait_for_timeout(400)
        menu = page.locator(f"[data-testid='status-menu-{MENU_CARD}']")
        options = await menu.locator("[data-status-option]").evaluate_all(
            "els => els.map(e => e.dataset.statusOption)"
        )
        log(
            f"17 「状态 ▾」展开状态下拉（{len(STATUS_OPTIONS)} 项 = 后端 LoopWorkspaceStatus 全集）",
            options == STATUS_OPTIONS,
            f"选项={options}",
        )

        current = await menu.locator("[data-status-option][data-current='true']").evaluate_all(
            "els => els.map(e => e.dataset.statusOption)"
        )
        log("18 下拉标出当前状态（卡片的真实后端状态）", current == ["active"], f"当前项={current}")

        b_before = {c: await badge(c) for c in ("doing", "review")}
        await menu.locator("[data-status-option='blocked']").click()
        menu_gone = await page.locator(f"[data-testid='status-menu-{MENU_CARD}']").count() == 0
        patched2 = await wait_api("PATCH", f"{API}/tasks/{MENU_CARD}")
        moved2 = await wait_card("review", MENU_CARD)
        log("19 下拉选择 → PATCH /api/v1/tasks/{id}，菜单收起", patched2 and menu_gone, "请求已发出")
        log("20 「阻塞 · 需返工」落入评审列", moved2, f"评审中列={await card_ids('review')}")

        rec2 = task_record(MENU_CARD)
        log(
            "21 HTTP 交叉核对：status=blocked 且 gate_status=blocked，标题保留",
            rec2.get("status") == "blocked"
            and rec2.get("gate_status") == "blocked"
            and rec2.get("title") == MENU_CARD_TITLE,
            f"status={rec2.get('status')} gate_status={rec2.get('gate_status')} title={rec2.get('title')!r}",
        )

        # ---------------- 阶段 5 · 审批门裁决：通过 / 打回 ----------------
        b_before = {c: await badge(c) for c in ("review", "done")}
        api_bodies.clear()
        await page.locator(f"[data-card-id='{SUBMIT_CARD}'] button:has-text('通过')").click()
        await page.wait_for_timeout(700)
        modal_text = await page.locator("body").inner_text()
        log(
            "22 评审列「通过」→ 打开审批门裁决模态（显示目标任务）",
            "审批门裁决" in modal_text and SUBMIT_CARD in modal_text,
            "模态显示目标任务",
        )
        await page.locator("textarea").last.fill("E2E：放行并执行")
        await page.locator("button:has-text('确认提交')").click()

        gated = await wait_api("POST", "/gate/decision")
        moved3 = await wait_card("done", SUBMIT_CARD)
        log("23 「确认提交」→ POST /api/v1/tasks/{id}/gate/decision", gated, "请求已发出")
        log("24 后端裁决回写改变了看板列位（评审中 → 已完成）", moved3, f"已完成列={await card_ids('done')}")

        b_after = {c: await badge(c) for c in ("review", "done")}
        log(
            "25 列头徽标同步（评审中 −1、已完成 +1）",
            b_after["review"] == b_before["review"] - 1 and b_after["done"] == b_before["done"] + 1,
            f"评审中 {b_before['review']}→{b_after['review']}，已完成 {b_before['done']}→{b_after['done']}",
        )

        rec3 = task_record(SUBMIT_CARD)
        log(
            "26 裁决保留任务标题（未被改写成裁决批注）",
            rec3.get("title") == SUBMIT_CARD_TITLE and rec3.get("status") == "completed",
            f"title={rec3.get('title')!r} status={rec3.get('status')}",
        )

        api_bodies.clear()
        await page.locator(f"[data-card-id='{MENU_CARD}'] button:has-text('打回')").click()
        await page.wait_for_timeout(700)
        await page.locator("textarea").last.fill("E2E：证据不足，打回返工")
        await page.locator("button:has-text('确认提交')").click()
        await page.wait_for_timeout(900)
        denial = next((b for b in api_bodies if b.get("decision")), None)
        log(
            "27 「打回」预选驳回并如实入请求体（decision=denied）",
            bool(denial) and denial.get("decision") == "denied",
            f"请求体={denial}",
        )
        rec4 = task_record(MENU_CARD)
        log(
            "28 打回后状态仍为 blocked（卡片留在评审列等待返工）",
            rec4.get("status") == "blocked" and MENU_CARD in await card_ids("review"),
            f"status={rec4.get('status')}",
        )

        # ---------------- 阶段 6 · SSE 实时性 ----------------
        before = await page.locator("[data-card-id]").count()
        _, body = http(
            "POST",
            f"{API}/projects/{PROJECT}/tasks",
            {"title": "外部 HTTP 注入的 SSE 探针任务", "template": "auto-research"},
        )
        probe_id = (body or {}).get("task", {}).get("id") if isinstance(body, dict) else None
        pushed, waited = False, 0
        while waited < 8000 and probe_id:
            if probe_id in await card_ids("doing"):
                pushed = True
                break
            await page.wait_for_timeout(250)
            waited += 250
        after = await page.locator("[data-card-id]").count()
        log(
            "29 外部 POST 后看板自动刷新（SSE 驱动，无需手刷）",
            pushed and after == before + 1,
            f"卡片 {before} → {after}，探针={'上板' if pushed else '未出现'}",
        )

        # ---------------- 阶段 7 · 右栏 / 详情 / 折叠 / 复制 ----------------
        await page.locator(f"[data-card-id='{GATE_CARD}']").click()
        await page.wait_for_timeout(500)
        aside_n = await page.locator("aside").count()
        insp = await page.locator("aside").nth(1).inner_text()
        log("30 单击卡片 → 右栏跟随选中", aside_n == 2 and GATE_CARD in insp, f"aside={aside_n}")

        await page.locator("[data-testid='inspector-close']").click()
        await page.wait_for_timeout(500)
        log("31 右栏 ✕ 折叠生效", await page.locator("aside").count() == 1, "aside 2 → 1")

        await page.keyboard.press("Meta+b")
        await page.wait_for_timeout(500)
        log("32 ⌘B 展开右栏", await page.locator("aside").count() == 2, "aside 1 → 2")

        await page.locator("button:has-text('查看详情')").first.click()
        await page.wait_for_timeout(900)
        detail = await page.locator("main").inner_text()
        in_detail = await page.locator("[data-testid='detail-back']").count() == 1
        cols_in_detail = await page.locator("[data-column]").count()
        log(
            "33 右栏「查看详情 →」进任务详情（看板被详情取代，带上被选中任务 id）",
            in_detail and cols_in_detail == 0 and GATE_CARD in detail,
            f"返回控件={in_detail} 详情里的看板列={cols_in_detail}",
        )

        copy_btn = page.locator("[data-testid='host-cmd-copy']")
        await copy_btn.click()
        await page.wait_for_timeout(400)
        try:
            clip = await page.evaluate("navigator.clipboard.readText()")
        except Exception as exc:  # noqa: BLE001
            clip = f"<read failed: {exc}>"
        copied_flag = await copy_btn.get_attribute("data-copied")
        btn_label = await copy_btn.inner_text()
        log(
            "34 「复制」写入真实剪贴板（内容 = 宿主命令 + 本任务绑定）",
            "/goal" in clip and GATE_CARD in clip,
            f"剪贴板={clip[:64]!r}",
        )
        log(
            "35 复制后按钮给出「已复制」反馈",
            copied_flag == "true" and "已复制" in btn_label,
            f"data-copied={copied_flag} 文案={btn_label!r}",
        )

        await page.wait_for_timeout(1600)
        log("36 反馈 1.5s 后复原为「复制」", "已复制" not in await copy_btn.inner_text(), "")

        await page.locator("[data-testid='detail-back']").click()
        await page.wait_for_timeout(700)
        back_cols = await page.locator("[data-column]").count()
        back_controls = await page.locator("[data-testid='detail-back']").count()
        log(
            "37 详情 ✕ 返回看板（四列回来，详情退场）",
            back_cols == 4 and back_controls == 0,
            f"列数={back_cols} 残留返回控件={back_controls}",
        )

        # ---------------- 阶段 8 · 契约边界 + 控制台 ----------------
        status_bad, _ = http("PATCH", f"{API}/tasks/{MENU_CARD}", {"status": "nope"})
        status_empty, _ = http("PATCH", f"{API}/tasks/{MENU_CARD}", {})
        malformed, _ = http("POST", f"{API}/projects/{PROJECT}/tasks", None)
        log(
            "38 网关守住契约边界：非法状态 / 空 PATCH / 畸形 body → 400",
            status_bad == 400 and status_empty == 400,
            f"bad status={status_bad}，空 body={status_empty}",
        )
        log("39 控制台零错误 / 零 pageerror", not console_errors, f"{console_errors[:3]}")

        await page.screenshot(path="/tmp/loopdesk-lifecycle/wired_board.png")
        await browser.close()

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"\n=== {passed}/{total} 通过 ===")
    print(f"本次走查前端发出的 /api 请求：{len(api_calls)} 条（验收基线：> 0）")
    for m, u in api_calls:
        print(f"  {m:4s} {u.replace(BASE, '')}")

    json.dump(
        {
            "passed": passed,
            "total": total,
            "results": [{"step": s, "ok": o, "detail": d} for s, o, d in RESULTS],
            "api_calls": [{"method": m, "url": u} for m, u in api_calls],
            "console_errors": console_errors,
        },
        open("/tmp/loopdesk-lifecycle/wired_report.json", "w"),
        ensure_ascii=False,
        indent=2,
    )
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
